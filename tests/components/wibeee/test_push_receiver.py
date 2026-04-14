"""Tests for Wibeee push receiver."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.wibeee.push_receiver import (
    PushReceiver,
    async_setup_push_receiver,
    parse_push_data,
)

from .conftest import MOCK_MAC, MOCK_PUSH_QUERY


# ---------------------------------------------------------------------------
# parse_push_data
# ---------------------------------------------------------------------------


def test_parse_push_data_single_phase() -> None:
    """Test parsing push data for a single phase device."""
    query = {
        "mac": "001ec0112233",
        "v1": "230.5",
        "i1": "2.3",
        "a1": "277",
        "e1": "12345",
    }
    result = parse_push_data(query)

    assert "fase1" in result
    assert result["fase1"]["vrms"] == "230.5"
    assert result["fase1"]["irms"] == "2.3"
    assert result["fase1"]["p_activa"] == "277"
    assert result["fase1"]["energia_activa"] == "12345"


def test_parse_push_data_three_phase() -> None:
    """Test parsing push data for a three phase device with totals."""
    query = {
        "mac": "001ec0112233",
        "v1": "230.5",
        "v2": "231.0",
        "v3": "229.8",
        "vt": "230.4",
        "a1": "100",
        "a2": "200",
        "a3": "150",
        "at": "450",
    }
    result = parse_push_data(query)

    assert len(result) == 4
    assert result["fase1"]["vrms"] == "230.5"
    assert result["fase2"]["vrms"] == "231.0"
    assert result["fase3"]["vrms"] == "229.8"
    assert result["fase4"]["vrms"] == "230.4"
    assert result["fase4"]["p_activa"] == "450"


def test_parse_push_data_all_sensors() -> None:
    """Test parsing all known sensor types."""
    query = {
        "v1": "230.5",
        "i1": "2.3",
        "p1": "530",
        "a1": "277",
        "r1": "120",
        "q1": "50.0",
        "f1": "0.98",
        "e1": "12345",
        "o1": "6789",
    }
    result = parse_push_data(query)
    fase1 = result["fase1"]

    assert fase1["vrms"] == "230.5"
    assert fase1["irms"] == "2.3"
    assert fase1["p_aparent"] == "530"
    assert fase1["p_activa"] == "277"
    assert fase1["p_reactiva_ind"] == "120"
    assert fase1["frecuencia"] == "50.0"
    assert fase1["factor_potencia"] == "0.98"
    assert fase1["energia_activa"] == "12345"
    assert fase1["energia_reactiva_ind"] == "6789"


def test_parse_push_data_ignores_unknown() -> None:
    """Test that unknown parameters are ignored."""
    query = {
        "mac": "001ec0112233",
        "v1": "230.5",
        "xyz": "999",
        "z1": "888",
    }
    result = parse_push_data(query)

    assert "fase1" in result
    assert len(result["fase1"]) == 1
    assert result["fase1"]["vrms"] == "230.5"


def test_parse_push_data_empty() -> None:
    """Test parsing empty query parameters."""
    result = parse_push_data({})
    assert result == {}


def test_parse_push_data_short_params() -> None:
    """Test that single-character params are ignored."""
    result = parse_push_data({"v": "230", "a": "277"})
    assert result == {}


# ---------------------------------------------------------------------------
# PushReceiver
# ---------------------------------------------------------------------------


def test_push_receiver_register_and_callback() -> None:
    """Test registering a device and receiving callbacks."""
    receiver = PushReceiver()
    callback = MagicMock()

    receiver.register_device("00:1E:C0:11:22:33", callback)
    assert receiver.device_count == 1

    listener = receiver.get_listener("001ec0112233")
    assert listener is callback


def test_push_receiver_unregister() -> None:
    """Test unregistering a device."""
    receiver = PushReceiver()
    callback = MagicMock()

    receiver.register_device(MOCK_MAC, callback)
    assert receiver.device_count == 1

    receiver.unregister_device(MOCK_MAC)
    assert receiver.device_count == 0
    assert receiver.get_listener(MOCK_MAC) is None


def test_push_receiver_multiple_devices() -> None:
    """Test registering multiple devices."""
    receiver = PushReceiver()
    cb1 = MagicMock()
    cb2 = MagicMock()

    receiver.register_device("001ec0112233", cb1)
    receiver.register_device("001ec0445566", cb2)
    assert receiver.device_count == 2

    assert receiver.get_listener("001ec0112233") is cb1
    assert receiver.get_listener("001ec0445566") is cb2


def test_push_receiver_mac_normalization() -> None:
    """Test that MAC addresses are normalized (no colons, lowercase)."""
    receiver = PushReceiver()
    callback = MagicMock()

    receiver.register_device("00:1E:C0:11:22:33", callback)
    assert receiver.get_listener("001ec0112233") is callback
    assert receiver.get_listener("00:1E:C0:11:22:33") is callback


def test_push_receiver_unknown_device() -> None:
    """Test that unknown devices return None."""
    receiver = PushReceiver()
    assert receiver.get_listener("001ec0999999") is None


# ---------------------------------------------------------------------------
# async_setup_push_receiver (idempotent)
# ---------------------------------------------------------------------------


async def test_setup_push_receiver_registers_views(
    hass: HomeAssistant,
    hass_client_no_auth,
) -> None:
    """Test that setup registers HTTP views and is idempotent."""
    # Set up the HTTP component so hass.http is available
    assert await async_setup_component(hass, "http", {"http": {}})
    await hass.async_block_till_done()

    # First call should register views
    receiver1 = async_setup_push_receiver(hass)
    assert receiver1 is not None
    assert receiver1.device_count == 0

    # Second call should return the same instance
    receiver2 = async_setup_push_receiver(hass)
    assert receiver1 is receiver2


# ---------------------------------------------------------------------------
# HTTP view integration tests
# ---------------------------------------------------------------------------


async def test_receiver_avg_endpoint(
    hass: HomeAssistant,
    hass_client_no_auth,
    mock_config_entry_push,
    mock_wibeee_api,
) -> None:
    """Test the /Wibeee/receiverAvg endpoint returns correct response."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    client = await hass_client_no_auth()

    # Build query string from MOCK_PUSH_QUERY
    query = "&".join(f"{k}={v}" for k, v in MOCK_PUSH_QUERY.items())
    resp = await client.get(f"/Wibeee/receiverAvg?{query}")

    assert resp.status == 200
    text = await resp.text()
    assert text == "<<<WBAVG "


async def test_receiver_endpoint(
    hass: HomeAssistant,
    hass_client_no_auth,
    mock_config_entry_push,
    mock_wibeee_api,
) -> None:
    """Test the /Wibeee/receiver endpoint."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    client = await hass_client_no_auth()
    resp = await client.get(f"/Wibeee/receiver?mac={MOCK_MAC}&v1=230.5")

    assert resp.status == 200
    text = await resp.text()
    assert text == "<<<WBAVG "


async def test_receiver_leap_endpoint(
    hass: HomeAssistant,
    hass_client_no_auth,
    mock_config_entry_push,
    mock_wibeee_api,
) -> None:
    """Test the /Wibeee/receiverLeap endpoint."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    client = await hass_client_no_auth()
    resp = await client.get(f"/Wibeee/receiverLeap?mac={MOCK_MAC}&v1=230.5")

    assert resp.status == 200
    text = await resp.text()
    assert text == "<<<WGRADIENT=007 "


async def test_receiver_no_mac(
    hass: HomeAssistant,
    hass_client_no_auth,
    mock_config_entry_push,
    mock_wibeee_api,
) -> None:
    """Test push endpoint with no MAC in query."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    client = await hass_client_no_auth()
    resp = await client.get("/Wibeee/receiverAvg?v1=230.5")

    assert resp.status == 200
    text = await resp.text()
    assert text == "<<<WBAVG "


async def test_receiver_unregistered_mac(
    hass: HomeAssistant,
    hass_client_no_auth,
) -> None:
    """Test push data from an unregistered device is silently accepted."""
    # Set up the HTTP component so hass.http is available
    assert await async_setup_component(hass, "http", {"http": {}})
    await hass.async_block_till_done()

    # Register views but don't set up any device
    async_setup_push_receiver(hass)

    client = await hass_client_no_auth()
    resp = await client.get("/Wibeee/receiverAvg?mac=001ec0999999&v1=230.5")

    assert resp.status == 200
    text = await resp.text()
    assert text == "<<<WBAVG "
