"""Tests for Wibeee API client (api.py).

Tests the actual HTTP client logic with aiohttp mocked responses,
covering XML parsing, retries, error paths, and hex port conversion.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from aiohttp import ClientSession

from custom_components.wibeee.api import WibeeeAPI, WibeeeDeviceInfo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(status: int = 200, text: str = "") -> MagicMock:
    """Create a mock aiohttp response."""
    resp = MagicMock()
    resp.status = status
    resp.text = AsyncMock(return_value=text)
    # Support async context manager
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


def _make_session(responses: list[MagicMock] | MagicMock | None = None) -> MagicMock:
    """Create a mock aiohttp ClientSession."""
    session = MagicMock(spec=ClientSession)
    if responses is None:
        responses = [_make_response()]
    if isinstance(responses, MagicMock):
        responses = [responses]
    session.get = MagicMock(side_effect=responses)
    return session


STATUS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<response>
  <model>WBT</model>
  <webversion>4.4.199</webversion>
  <time>1570484447</time>
  <fase1_vrms>230.50</fase1_vrms>
  <fase1_irms>2.30</fase1_irms>
  <fase1_p_activa>277.00</fase1_p_activa>
  <fase1_energia_activa>12345</fase1_energia_activa>
  <fase4_vrms>230.50</fase4_vrms>
  <fase4_p_activa>277.00</fase4_p_activa>
</response>
"""

DEVICES_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<devices><id>WIBEEE</id></devices>
"""

VALUES_MAC_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<values>
  <variable><id>macAddr</id><value>00:1E:C0:11:22:33</value></variable>
</values>
"""

VALUES_SOFT_VERSION_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<values>
  <variable><id>softVersion</id><value>4.4.199</value></variable>
</values>
"""

VALUES_SERVER_IP_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<values>
  <variable><id>serverIP</id><value>192.168.1.50</value></variable>
</values>
"""

VALUES_SERVER_PORT_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<values>
  <variable><id>serverPort</id><value>1fbb</value></variable>
</values>
"""


# ---------------------------------------------------------------------------
# WibeeeDeviceInfo tests
# ---------------------------------------------------------------------------


class TestWibeeeDeviceInfo:
    """Tests for WibeeeDeviceInfo properties."""

    def test_mac_addr_formatted(self) -> None:
        info = WibeeeDeviceInfo("WB", "00:1E:C0:11:22:33", "WBT", "4.4", "1.2.3.4")
        assert info.mac_addr_formatted == "001ec0112233"

    def test_mac_addr_formatted_already_clean(self) -> None:
        info = WibeeeDeviceInfo("WB", "001ec0112233", "WBT", "4.4", "1.2.3.4")
        assert info.mac_addr_formatted == "001ec0112233"

    def test_mac_addr_short(self) -> None:
        info = WibeeeDeviceInfo("WB", "001ec0112233", "WBT", "4.4", "1.2.3.4")
        assert info.mac_addr_short == "112233"

    def test_mac_addr_short_uppercase(self) -> None:
        info = WibeeeDeviceInfo("WB", "001ec0aabbcc", "WBT", "4.4", "1.2.3.4")
        assert info.mac_addr_short == "AABBCC"


# ---------------------------------------------------------------------------
# async_fetch_url tests
# ---------------------------------------------------------------------------


class TestAsyncFetchUrl:
    """Tests for the core HTTP fetcher with retries."""

    @pytest.mark.asyncio
    async def test_success(self) -> None:
        session = _make_session([_make_response(200, "OK")])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_url("http://192.168.1.30/test")
        assert result == "OK"

    @pytest.mark.asyncio
    async def test_http_error_no_retry(self) -> None:
        session = _make_session([_make_response(500, "error")])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_url("http://x/test", retries=0)
        assert result is None

    @pytest.mark.asyncio
    async def test_http_error_with_retry_then_success(self) -> None:
        session = _make_session(
            [
                _make_response(500, ""),
                _make_response(200, "OK"),
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_url("http://x/test", retries=1)
        assert result == "OK"

    @pytest.mark.asyncio
    async def test_client_error_no_retry(self) -> None:
        resp = MagicMock()
        resp.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError("conn failed"))
        resp.__aexit__ = AsyncMock(return_value=False)
        session = _make_session([resp])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_url("http://x/test", retries=0)
        assert result is None

    @pytest.mark.asyncio
    async def test_timeout_error(self) -> None:
        resp = MagicMock()
        resp.__aenter__ = AsyncMock(side_effect=asyncio.TimeoutError())
        resp.__aexit__ = AsyncMock(return_value=False)
        session = _make_session([resp])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_url("http://x/test", retries=0)
        assert result is None

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self) -> None:
        """All retries fail -> returns None."""
        session = _make_session(
            [
                _make_response(503, ""),
                _make_response(503, ""),
                _make_response(503, ""),
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_url("http://x/test", retries=2)
        assert result is None


# ---------------------------------------------------------------------------
# async_fetch_status tests
# ---------------------------------------------------------------------------


class TestAsyncFetchStatus:
    """Tests for status.xml parsing."""

    @pytest.mark.asyncio
    async def test_success(self) -> None:
        session = _make_session([_make_response(200, STATUS_XML)])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_status(retries=0)
        assert result is not None
        assert result["model"] == "WBT"
        assert result["webversion"] == "4.4.199"
        assert result["fase1_vrms"] == "230.50"

    @pytest.mark.asyncio
    async def test_no_response(self) -> None:
        session = _make_session([_make_response(404, "")])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_status(retries=0)
        assert result is None

    @pytest.mark.asyncio
    async def test_malformed_xml(self) -> None:
        session = _make_session([_make_response(200, "<not>valid<xml")])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_status(retries=0)
        assert result is None

    @pytest.mark.asyncio
    async def test_no_response_tag(self) -> None:
        session = _make_session([_make_response(200, "<other><data>1</data></other>")])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_status(retries=0)
        assert result is None


# ---------------------------------------------------------------------------
# async_fetch_sensors_data tests
# ---------------------------------------------------------------------------


class TestAsyncFetchSensorsData:
    """Tests for sensor data parsing from status.xml."""

    @pytest.mark.asyncio
    async def test_parses_phases(self) -> None:
        session = _make_session([_make_response(200, STATUS_XML)])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_sensors_data(retries=0)
        assert result is not None
        assert "fase1" in result
        assert "fase4" in result
        assert result["fase1"]["vrms"] == "230.50"
        assert result["fase1"]["p_activa"] == "277.00"
        assert result["fase4"]["vrms"] == "230.50"

    @pytest.mark.asyncio
    async def test_no_data(self) -> None:
        session = _make_session([_make_response(500, "")])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_sensors_data(retries=0)
        assert result is None

    @pytest.mark.asyncio
    async def test_no_fase_keys(self) -> None:
        xml = "<response><model>WBT</model><webversion>1.0</webversion></response>"
        session = _make_session([_make_response(200, xml)])
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_fetch_sensors_data(retries=0)
        assert result is None


# ---------------------------------------------------------------------------
# async_fetch_device_info tests
# ---------------------------------------------------------------------------


class TestAsyncFetchDeviceInfo:
    """Tests for device info fetching (multi-step)."""

    @pytest.mark.asyncio
    async def test_full_info(self) -> None:
        """All requests succeed - returns complete device info."""
        session = _make_session(
            [
                _make_response(200, STATUS_XML),  # status.xml
                _make_response(200, DEVICES_XML),  # devices.xml
                _make_response(200, VALUES_MAC_XML),  # values.xml?var=WIBEEE.macAddr
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        info = await api.async_fetch_device_info(retries=0)
        assert info is not None
        assert info.model == "WBT"
        assert info.firmware_version == "4.4.199"
        assert info.wibeee_id == "WIBEEE"
        assert info.mac_addr == "001ec0112233"

    @pytest.mark.asyncio
    async def test_no_mac_returns_none(self) -> None:
        """If MAC can't be determined, returns None."""
        session = _make_session(
            [
                _make_response(200, STATUS_XML),  # status
                _make_response(200, DEVICES_XML),  # devices
                _make_response(404, ""),  # values (MAC) -> fail
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        info = await api.async_fetch_device_info(retries=0)
        assert info is None

    @pytest.mark.asyncio
    async def test_status_fails_uses_fallbacks(self) -> None:
        """If status.xml fails, model comes from web scraping, firmware from values."""
        web_page = '<html><script>var model = "WBB";</script></html>'
        session = _make_session(
            [
                _make_response(500, ""),  # status.xml fails
                _make_response(200, DEVICES_XML),  # devices.xml
                _make_response(200, VALUES_MAC_XML),  # values.xml (MAC)
                _make_response(200, ""),  # login redirect (model scrape)
                _make_response(200, web_page),  # index.html (model scrape)
                _make_response(200, VALUES_SOFT_VERSION_XML),  # values (firmware)
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        info = await api.async_fetch_device_info(retries=0)
        assert info is not None
        assert info.model == "WBB"
        assert info.firmware_version == "4.4.199"


# ---------------------------------------------------------------------------
# async_check_connection tests
# ---------------------------------------------------------------------------


class TestAsyncCheckConnection:
    """Tests for connection check."""

    @pytest.mark.asyncio
    async def test_wibeee_title(self) -> None:
        html = "<html><title>WiBeee</title></html>"
        session = _make_session([_make_response(200, html)])
        api = WibeeeAPI(session, "192.168.1.30")
        assert await api.async_check_connection() is True

    @pytest.mark.asyncio
    async def test_wibeee_in_body(self) -> None:
        html = "<html><body>Welcome to WiBeee monitor</body></html>"
        session = _make_session([_make_response(200, html)])
        api = WibeeeAPI(session, "192.168.1.30")
        assert await api.async_check_connection() is True

    @pytest.mark.asyncio
    async def test_not_wibeee(self) -> None:
        html = "<html><title>Other Device</title></html>"
        session = _make_session([_make_response(200, html)])
        api = WibeeeAPI(session, "192.168.1.30")
        assert await api.async_check_connection() is False

    @pytest.mark.asyncio
    async def test_no_response(self) -> None:
        # async_check_connection uses retries=1, so we need 2 responses
        session = _make_session(
            [
                _make_response(500, ""),
                _make_response(500, ""),
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        assert await api.async_check_connection() is False


# ---------------------------------------------------------------------------
# async_configure_push_server tests
# ---------------------------------------------------------------------------


class TestAsyncConfigurePushServer:
    """Tests for push server configuration."""

    @pytest.mark.asyncio
    async def test_success(self) -> None:
        session = _make_session(
            [
                _make_response(200, "OK"),  # configura_server
                _make_response(200, "OK"),  # config_value?reset=true
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_configure_push_server("192.168.1.50", 8123)
        assert result is True

    @pytest.mark.asyncio
    async def test_hex_port_in_url(self) -> None:
        """Verify port is sent as 4-char hex."""
        session = _make_session(
            [
                _make_response(200, "OK"),
                _make_response(200, "OK"),
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        await api.async_configure_push_server("192.168.1.50", 8123)

        # 8123 decimal = 1fbb hex
        call_args = session.get.call_args_list[0]
        url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
        assert "portServidor=1fbb" in url

    @pytest.mark.asyncio
    async def test_hex_port_8600(self) -> None:
        """8600 = 2198 hex."""
        session = _make_session(
            [
                _make_response(200, "OK"),
                _make_response(200, "OK"),
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        await api.async_configure_push_server("10.0.0.1", 8600)

        call_args = session.get.call_args_list[0]
        url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
        assert "portServidor=2198" in url

    @pytest.mark.asyncio
    async def test_config_fails(self) -> None:
        # async_configure_push_server uses retries=2 (3 total attempts)
        session = _make_session(
            [
                _make_response(500, ""),
                _make_response(500, ""),
                _make_response(500, ""),
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_configure_push_server("192.168.1.50", 8123)
        assert result is False


# ---------------------------------------------------------------------------
# async_reboot / async_reset_energy tests
# ---------------------------------------------------------------------------


class TestDeviceActions:
    """Tests for reboot and reset energy actions."""

    @pytest.mark.asyncio
    async def test_reboot_success(self) -> None:
        session = _make_session([_make_response(200, "OK")])
        api = WibeeeAPI(session, "192.168.1.30")
        assert await api.async_reboot() is True

    @pytest.mark.asyncio
    async def test_reboot_failure(self) -> None:
        session = _make_session([_make_response(500, "")])
        api = WibeeeAPI(session, "192.168.1.30")
        assert await api.async_reboot() is False

    @pytest.mark.asyncio
    async def test_reboot_url(self) -> None:
        session = _make_session([_make_response(200, "OK")])
        api = WibeeeAPI(session, "192.168.1.30")
        await api.async_reboot()
        url = session.get.call_args_list[0][0][0]
        assert url == "http://192.168.1.30:80/config_value?reboot=1"

    @pytest.mark.asyncio
    async def test_reset_energy_success(self) -> None:
        session = _make_session([_make_response(200, "OK")])
        api = WibeeeAPI(session, "192.168.1.30")
        assert await api.async_reset_energy() is True

    @pytest.mark.asyncio
    async def test_reset_energy_failure(self) -> None:
        session = _make_session([_make_response(500, "")])
        api = WibeeeAPI(session, "192.168.1.30")
        assert await api.async_reset_energy() is False

    @pytest.mark.asyncio
    async def test_reset_energy_url(self) -> None:
        session = _make_session([_make_response(200, "OK")])
        api = WibeeeAPI(session, "192.168.1.30")
        await api.async_reset_energy()
        url = session.get.call_args_list[0][0][0]
        assert url == "http://192.168.1.30:80/resetEnergy?resetEn=1"


# ---------------------------------------------------------------------------
# async_get_push_server_config tests
# ---------------------------------------------------------------------------


class TestAsyncGetPushServerConfig:
    """Tests for reading push server configuration."""

    @pytest.mark.asyncio
    async def test_success(self) -> None:
        session = _make_session(
            [
                _make_response(200, DEVICES_XML),  # _fetch_device_id
                _make_response(200, VALUES_SERVER_IP_XML),  # serverIP
                _make_response(200, VALUES_SERVER_PORT_XML),  # serverPort
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_get_push_server_config()
        assert result is not None
        assert result["server_ip"] == "192.168.1.50"
        assert result["server_port"] == 8123  # 0x1fbb = 8123

    @pytest.mark.asyncio
    async def test_invalid_hex_port(self) -> None:
        bad_port_xml = "<values><variable><id>serverPort</id><value>ZZZZ</value></variable></values>"
        session = _make_session(
            [
                _make_response(200, DEVICES_XML),
                _make_response(200, VALUES_SERVER_IP_XML),
                _make_response(200, bad_port_xml),
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_get_push_server_config()
        assert result is not None
        assert result["server_port"] == 0

    @pytest.mark.asyncio
    async def test_missing_ip(self) -> None:
        # _fetch_device_id(retries=1) -> async_fetch_url(retries=1): succeeds on 1st try (1 resp)
        # _fetch_value("serverIP", retries=1) -> async_fetch_url(retries=1): 2 attempts = 2 responses
        # _fetch_value("serverPort", retries=1) -> async_fetch_url(retries=1): 2 attempts = 2 responses
        # Both fetches happen before the `if server_ip and server_port_hex` guard
        session = _make_session(
            [
                _make_response(200, DEVICES_XML),  # _fetch_device_id - success
                _make_response(404, ""),  # serverIP attempt 1
                _make_response(404, ""),  # serverIP attempt 2 (retry)
                _make_response(200, VALUES_SERVER_PORT_XML),  # serverPort attempt 1
            ]
        )
        api = WibeeeAPI(session, "192.168.1.30")
        result = await api.async_get_push_server_config()
        assert result is None


# ---------------------------------------------------------------------------
# base_url / init tests
# ---------------------------------------------------------------------------


class TestAPIInit:
    """Tests for API initialization."""

    def test_base_url_default_port(self) -> None:
        api = WibeeeAPI(MagicMock(), "192.168.1.30")
        assert api.base_url == "http://192.168.1.30:80"

    def test_base_url_custom_port(self) -> None:
        api = WibeeeAPI(MagicMock(), "192.168.1.30", port=8080)
        assert api.base_url == "http://192.168.1.30:8080"

    def test_custom_timeout(self) -> None:
        api = WibeeeAPI(MagicMock(), "192.168.1.30", timeout=timedelta(seconds=30))
        assert api.timeout.total == 30.0
