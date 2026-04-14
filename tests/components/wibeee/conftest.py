"""Test fixtures for Wibeee integration."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.wibeee.api import WibeeeDeviceInfo
from custom_components.wibeee.const import (
    CONF_MAC_ADDRESS,
    CONF_SCAN_INTERVAL,
    CONF_UPDATE_MODE,
    CONF_WIBEEE_ID,
    DOMAIN,
    MODE_LOCAL_PUSH,
    MODE_POLLING,
)

# ---------------------------------------------------------------------------
# Mock data constants
# ---------------------------------------------------------------------------

MOCK_HOST = "192.168.1.100"
MOCK_MAC = "001ec0112233"
MOCK_WIBEEE_ID = "WIBEEE"
MOCK_MODEL = "WBT"
MOCK_FIRMWARE = "4.4.199"

MOCK_DEVICE_INFO = WibeeeDeviceInfo(
    wibeee_id=MOCK_WIBEEE_ID,
    mac_addr=MOCK_MAC,
    model=MOCK_MODEL,
    firmware_version=MOCK_FIRMWARE,
    ip_addr=MOCK_HOST,
)

MOCK_SENSOR_DATA = {
    "fase1": {
        "vrms": "230.50",
        "irms": "2.30",
        "p_activa": "277.00",
        "p_aparent": "530.00",
        "p_reactiva_ind": "120.00",
        "frecuencia": "50.01",
        "factor_potencia": "0.98",
        "energia_activa": "12345",
    },
    "fase4": {
        "vrms": "230.50",
        "irms": "2.30",
        "p_activa": "277.00",
        "energia_activa": "12345",
    },
}

MOCK_STATUS_XML = {
    "fase1_vrms": "230.50",
    "fase1_irms": "2.30",
    "fase1_p_activa": "277.00",
    "fase1_p_aparent": "530.00",
    "fase1_p_reactiva_ind": "120.00",
    "fase1_frecuencia": "50.01",
    "fase1_factor_potencia": "0.98",
    "fase1_energia_activa": "12345",
    "fase4_vrms": "230.50",
    "fase4_irms": "2.30",
    "fase4_p_activa": "277.00",
    "fase4_energia_activa": "12345",
    "model": MOCK_MODEL,
    "webversion": MOCK_FIRMWARE,
}

# Simulates a push query string from the WiBeee device
MOCK_PUSH_QUERY = {
    "mac": MOCK_MAC,
    "v1": "230.50",
    "i1": "2.30",
    "a1": "277.00",
    "p1": "530.00",
    "r1": "120.00",
    "q1": "50.01",
    "f1": "0.98",
    "e1": "12345",
    "vt": "230.50",
    "it": "2.30",
    "at": "277.00",
    "et": "12345",
}


# ---------------------------------------------------------------------------
# Config entry fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_config_entry_push() -> MockConfigEntry:
    """Create a mock config entry for local push mode."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_MAC,
        title="Wibeee 2233",
        data={
            "host": MOCK_HOST,
            CONF_MAC_ADDRESS: MOCK_MAC,
            CONF_WIBEEE_ID: MOCK_WIBEEE_ID,
        },
        options={
            CONF_UPDATE_MODE: MODE_LOCAL_PUSH,
        },
        version=2,
    )


@pytest.fixture
def mock_config_entry_polling() -> MockConfigEntry:
    """Create a mock config entry for polling mode."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_MAC,
        title="Wibeee 2233",
        data={
            "host": MOCK_HOST,
            CONF_MAC_ADDRESS: MOCK_MAC,
            CONF_WIBEEE_ID: MOCK_WIBEEE_ID,
        },
        options={
            CONF_UPDATE_MODE: MODE_POLLING,
            CONF_SCAN_INTERVAL: 30,
        },
        version=2,
    )


# ---------------------------------------------------------------------------
# API mock fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_wibeee_api() -> Generator[MagicMock]:
    """Mock the WibeeeAPI class for sensor/init tests."""
    with patch(
        "custom_components.wibeee.sensor.WibeeeAPI", autospec=True
    ) as mock_cls:
        api = mock_cls.return_value
        api.async_check_connection = AsyncMock(return_value=True)
        api.async_fetch_device_info = AsyncMock(return_value=MOCK_DEVICE_INFO)
        api.async_fetch_sensors_data = AsyncMock(return_value=MOCK_SENSOR_DATA)
        api.async_fetch_status = AsyncMock(return_value=MOCK_STATUS_XML)
        api.async_configure_push_server = AsyncMock(return_value=True)
        api.host = MOCK_HOST
        yield api


@pytest.fixture
def mock_wibeee_api_config_flow() -> Generator[MagicMock]:
    """Mock the WibeeeAPI class specifically for config flow tests."""
    with patch(
        "custom_components.wibeee.config_flow.WibeeeAPI", autospec=True
    ) as mock_cls:
        api = mock_cls.return_value
        api.async_check_connection = AsyncMock(return_value=True)
        api.async_fetch_device_info = AsyncMock(return_value=MOCK_DEVICE_INFO)
        api.async_fetch_sensors_data = AsyncMock(return_value=MOCK_SENSOR_DATA)
        api.async_fetch_status = AsyncMock(return_value=MOCK_STATUS_XML)
        api.async_configure_push_server = AsyncMock(return_value=True)
        api.host = MOCK_HOST
        yield api


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry for config flow tests."""
    with patch(
        "custom_components.wibeee.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup
