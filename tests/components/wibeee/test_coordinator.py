"""Tests for WibeeeCoordinator."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import aiohttp
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


async def test_coordinator_default_name_uses_host(hass: HomeAssistant) -> None:
    """When no name is provided, coordinator uses Wibeee + host."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(hass, api)

    assert coordinator.name == f"Wibeee {MOCK_HOST}"


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


async def test_async_update_data_timeout_raises_update_failed(
    hass: HomeAssistant,
) -> None:
    """_async_update_data wraps asyncio.TimeoutError in UpdateFailed."""
    api = _make_api_mock(side_effect=asyncio.TimeoutError())
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    with pytest.raises(UpdateFailed, match="Error fetching data"):
        await coordinator._async_update_data()


async def test_async_update_data_client_error_raises_update_failed(
    hass: HomeAssistant,
) -> None:
    """_async_update_data wraps aiohttp.ClientError in UpdateFailed."""
    api = _make_api_mock(side_effect=aiohttp.ClientError("Connection refused"))
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    with pytest.raises(UpdateFailed, match="Error fetching data"):
        await coordinator._async_update_data()


async def test_async_update_data_invalid_format_raises_update_failed(
    hass: HomeAssistant,
) -> None:
    """_async_update_data raises UpdateFailed if data is not a dict."""
    api = _make_api_mock(sensor_data="not a dict")  # type: ignore[arg-type]
    coordinator = WibeeeCoordinator(
        hass, api, name="Wibeee", update_interval=timedelta(seconds=30)
    )

    with pytest.raises(UpdateFailed, match="Invalid data format"):
        await coordinator._async_update_data()


# ---------------------------------------------------------------------------
# async_push_update – push mode public API
# ---------------------------------------------------------------------------


async def test_push_update_injects_data(hass: HomeAssistant) -> None:
    """async_push_update injects data into coordinator."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(hass, api, name="Wibeee push", update_interval=None)

    assert coordinator.data is None

    coordinator.async_push_update(MOCK_SENSOR_DATA)

    assert coordinator.data == MOCK_SENSOR_DATA


async def test_push_update_overwrites_previous(hass: HomeAssistant) -> None:
    """Successive push updates replace previous data."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(hass, api, name="Wibeee push", update_interval=None)

    first_data = {"fase1": {"vrms": "230.00"}}
    second_data = {"fase1": {"vrms": "231.50"}}

    coordinator.async_push_update(first_data)
    assert coordinator.data == first_data

    coordinator.async_push_update(second_data)
    assert coordinator.data == second_data


async def test_push_update_ignores_invalid_data(hass: HomeAssistant, caplog) -> None:
    """async_push_update ignores non-dict data and logs warning."""
    api = _make_api_mock()
    coordinator = WibeeeCoordinator(hass, api, name="Wibeee push", update_interval=None)

    coordinator.async_push_update("bad data")  # type: ignore[arg-type]

    assert coordinator.data is None
    assert "invalid push data" in caplog.text.lower()


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
