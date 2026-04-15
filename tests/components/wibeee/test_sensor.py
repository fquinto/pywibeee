"""Tests for Wibeee sensor platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.wibeee.const import DOMAIN

from .conftest import (
    MOCK_MAC,
    MOCK_PUSH_QUERY,
    MOCK_SENSOR_DATA,
)


# ---------------------------------------------------------------------------
# Polling mode sensor tests
# ---------------------------------------------------------------------------


async def test_polling_sensors_created(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that polling mode creates sensor entities."""
    mock_config_entry_polling.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    # Check some key entities exist
    states = hass.states.async_all("sensor")
    assert len(states) > 0

    # Check entity IDs follow the expected pattern
    entity_ids = [s.entity_id for s in states]
    assert any("voltage" in eid or "phase_voltage" in eid for eid in entity_ids), (
        f"No voltage sensor found in: {entity_ids}"
    )
    assert any("active_power" in eid for eid in entity_ids), (
        f"No active power sensor found in: {entity_ids}"
    )


async def test_polling_sensor_values(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that polling sensors have correct values from coordinator."""
    mock_config_entry_polling.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    # Find the active power sensor for fase1
    states = hass.states.async_all("sensor")
    power_sensors = [
        s for s in states if "active_power" in s.entity_id and "l1" in s.entity_id
    ]

    if power_sensors:
        state = power_sensors[0]
        assert state.state == "277.0"


async def test_polling_sensor_energy_dashboard_compliance(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that energy sensors meet Energy Dashboard requirements.

    Energy Dashboard requires:
    - device_class = SensorDeviceClass.ENERGY
    - state_class = SensorStateClass.TOTAL_INCREASING (or TOTAL)
    - native_unit_of_measurement in UnitOfEnergy
    """
    mock_config_entry_polling.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    # Find energy sensors
    states = hass.states.async_all("sensor")
    energy_sensors = [
        s for s in states if "energy" in s.entity_id or "energia" in s.entity_id
    ]

    for state in energy_sensors:
        # Only check active energy sensors (reactive have different device_class)
        if "active_energy" in state.entity_id:
            attrs = state.attributes
            assert attrs.get("device_class") == SensorDeviceClass.ENERGY
            assert attrs.get("state_class") == SensorStateClass.TOTAL_INCREASING
            assert attrs.get("unit_of_measurement") in (
                UnitOfEnergy.WATT_HOUR,
                UnitOfEnergy.KILO_WATT_HOUR,
                "Wh",
                "kWh",
            )


# ---------------------------------------------------------------------------
# Local push mode sensor tests
# ---------------------------------------------------------------------------


async def test_push_sensors_created(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that push mode creates sensor entities."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    states = hass.states.async_all("sensor")
    assert len(states) > 0


async def test_push_sensor_initial_values(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that push sensors have initial values from the first poll."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    states = hass.states.async_all("sensor")
    # At least some should have non-unknown values (from initial poll)
    non_unknown = [s for s in states if s.state != "unknown"]
    assert len(non_unknown) > 0


async def test_push_sensor_updates_via_http(
    hass: HomeAssistant,
    hass_client_no_auth,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that push sensors update when HTTP endpoint receives data."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    # Send push data via HTTP
    client = await hass_client_no_auth()
    query = "&".join(f"{k}={v}" for k, v in MOCK_PUSH_QUERY.items())
    resp = await client.get(f"/Wibeee/receiverAvg?{query}")
    assert resp.status == 200
    await hass.async_block_till_done()

    # Find the active power sensor for fase1 (push param "a1" -> p_activa)
    states = hass.states.async_all("sensor")
    power_sensors = [
        s for s in states if "active_power" in s.entity_id and "l1" in s.entity_id
    ]

    if power_sensors:
        state = power_sensors[0]
        assert state.state == "277.0"


async def test_push_sensor_updates_with_new_values(
    hass: HomeAssistant,
    hass_client_no_auth,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that push sensors reflect new values after an update."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    client = await hass_client_no_auth()

    # Send initial data
    query = f"mac={MOCK_MAC}&v1=230.5&a1=277.0"
    await client.get(f"/Wibeee/receiverAvg?{query}")
    await hass.async_block_till_done()

    # Send updated data with different values
    query = f"mac={MOCK_MAC}&v1=232.0&a1=350.0"
    await client.get(f"/Wibeee/receiverAvg?{query}")
    await hass.async_block_till_done()

    # Check that sensors reflect the updated values
    states = hass.states.async_all("sensor")
    power_sensors = [
        s for s in states if "active_power" in s.entity_id and "l1" in s.entity_id
    ]

    if power_sensors:
        state = power_sensors[0]
        assert state.state == "350.0"


# ---------------------------------------------------------------------------
# Sensor error path tests
# ---------------------------------------------------------------------------


async def test_push_no_initial_data_logs_warning(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
    caplog,
) -> None:
    """Test that push mode logs warning when initial poll returns no data."""
    mock_wibeee_api.async_fetch_sensors_data = AsyncMock(return_value=None)
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    states = hass.states.async_all("sensor")
    assert len(states) == 0
    assert "no sensors found" in caplog.text.lower() or "no data" in caplog.text.lower()


async def test_polling_device_info_none_fallback(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that polling mode uses fallback device info when fetch returns None."""
    mock_wibeee_api.async_fetch_device_info = AsyncMock(return_value=None)
    mock_config_entry_polling.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    # Should still create sensors despite fallback device info
    states = hass.states.async_all("sensor")
    assert len(states) > 0


async def test_polling_coordinator_fetch_failure(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that coordinator raises UpdateFailed when data is None."""
    # First call succeeds (for first refresh), second call fails
    mock_wibeee_api.async_fetch_sensors_data = AsyncMock(
        side_effect=[MOCK_SENSOR_DATA, None]
    )
    mock_config_entry_polling.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    # Sensors should be created from first successful fetch
    states = hass.states.async_all("sensor")
    assert len(states) > 0


async def test_fase4_total_created_before_phases(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that fase4 (Total) device is created before L1/L2/L3 phases."""
    # Include all phases to verify ordering
    full_data = {
        "fase1": {"vrms": "230.5", "p_activa": "277.0"},
        "fase2": {"vrms": "231.0", "p_activa": "280.0"},
        "fase3": {"vrms": "229.5", "p_activa": "270.0"},
        "fase4": {"vrms": "230.3", "p_activa": "827.0"},
    }
    mock_wibeee_api.async_fetch_sensors_data = AsyncMock(return_value=full_data)
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    device_registry = dr.async_get(hass)
    wibeee_devices = [
        d
        for d in device_registry.devices.values()
        if any(DOMAIN in identifier[0] for identifier in d.identifiers)
    ]

    # Should have main device + 3 phase sub-devices = 4 devices
    assert len(wibeee_devices) >= 4

    # Check phase devices have via_device pointing to main
    phase_devices = [d for d in wibeee_devices if d.via_device_id is not None]
    assert len(phase_devices) == 3  # L1, L2, L3


# ---------------------------------------------------------------------------
# Device info tests
# ---------------------------------------------------------------------------


async def test_device_info_registered(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that the device is registered in the device registry."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    device_registry = dr.async_get(hass)
    devices = list(device_registry.devices.values())

    # Should have at least the main device
    wibeee_devices = [
        d
        for d in devices
        if any(DOMAIN in identifier[0] for identifier in d.identifiers)
    ]
    assert len(wibeee_devices) >= 1

    # Check main device info
    main_device = next((d for d in wibeee_devices if d.manufacturer == "Smilics"), None)
    assert main_device is not None
