"""Tests for WibeeeCoordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.wibeee.coordinator import WibeeeCoordinator

from .conftest import MOCK_HOST, MOCK_SENSOR_DATA


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_api_mock(
    *,
    sensor_data: dict | None = MOCK_SENSOR_DATA,
    side_effect: Exception | None = None,
) -> MagicMock:
    """Build a minimal WibeeeAPI mock for coordinator tests."""
    api = MagicMock()
    api.host = MOCK_HOST
    if side_effect is not None:
        api.async_fetch_sensors_data = AsyncMock(side_effect=side_effect)
    else:
        api.async_fetch_sensors_data = AsyncMock(return_value=sensor_data)
    return api


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


async def test_coordinator_init_polling(hass: HomeAssistant) -> None:
    """Polling coordinator stores api and update_interval."""
    api = _make_api_mock()
    interval = timedelta(seconds=30)
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee test", update_interval=interval
    )

    assert coordinator.api is api
    assert coordinator.update_interval == interval
    assert coordinator.name == "Wibeee test"


async def test_coordinator_init_push(hass: HomeAssistant) -> None:
    """Push coordinator has update_interval=None."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(hass, api, name="Wibeee push", update_interval=None)

    assert coordinator.api is api
    assert coordinator.update_interval is None


# ---------------------------------------------------------------------------
# _async_update_data – success path
# ---------------------------------------------------------------------------


async def test_async_update_data_returns_sensor_data(hass: HomeAssistant) -> None:
    """_async_update_data returns the data from the API."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    data = await coordinator._async_update_data()

    assert data == MOCK_SENSOR_DATA
    api.async_fetch_sensors_data.assert_awaited_once_with(retries=2)


# ---------------------------------------------------------------------------
# _async_update_data – error paths
# ---------------------------------------------------------------------------


async def test_async_update_data_none_raises_update_failed(
    hass: HomeAssistant,
) -> None:
    """_async_update_data raises UpdateFailed when API returns None."""
    api = _make_api_mock(sensor_data=None)
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    with pytest.raises(UpdateFailed, match="No data received"):
        await coordinator._async_update_data()


async def test_async_update_data_api_exception_raises_update_failed(
    hass: HomeAssistant,
) -> None:
    """_async_update_data wraps API exceptions in UpdateFailed."""
    api = _make_api_mock(side_effect=TimeoutError("Device unreachable"))
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    with pytest.raises(UpdateFailed, match="Error fetching data"):
        await coordinator._async_update_data()


async def test_async_update_data_connection_error(hass: HomeAssistant) -> None:
    """_async_update_data wraps ConnectionError in UpdateFailed."""
    api = _make_api_mock(side_effect=ConnectionError("Connection refused"))
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    with pytest.raises(UpdateFailed, match="Error fetching data"):
        await coordinator._async_update_data()


# ---------------------------------------------------------------------------
# async_set_updated_data – push mode injection
# ---------------------------------------------------------------------------


async def test_push_mode_set_updated_data(hass: HomeAssistant) -> None:
    """async_set_updated_data injects data in push mode."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(hass, api, name="Wibeee push", update_interval=None)

    assert coordinator.data is None

    coordinator.async_set_updated_data(MOCK_SENSOR_DATA)

    assert coordinator.data == MOCK_SENSOR_DATA


async def test_push_mode_updates_overwrite_previous(hass: HomeAssistant) -> None:
    """Successive push updates replace previous data."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(hass, api, name="Wibeee push", update_interval=None)

    first_data = {"fase1": {"vrms": "230.00"}}
    second_data = {"fase1": {"vrms": "231.50"}}

    coordinator.async_set_updated_data(first_data)
    assert coordinator.data == first_data

    coordinator.async_set_updated_data(second_data)
    assert coordinator.data == second_data


# ---------------------------------------------------------------------------
# Integration: manual refresh via HA coordinator machinery
# ---------------------------------------------------------------------------


async def test_async_refresh_populates_data(hass: HomeAssistant) -> None:
    """async_refresh populates coordinator.data on success."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    await coordinator.async_refresh()

    assert coordinator.data == MOCK_SENSOR_DATA
    assert coordinator.last_update_success is True


async def test_async_refresh_failure_sets_last_update_false(
    hass: HomeAssistant,
) -> None:
    """async_refresh marks last_update_success=False on failure."""
    api = _make_api_mock(sensor_data=None)
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    await coordinator.async_refresh()

    assert coordinator.data is None
    assert coordinator.last_update_success is False
