"""Tests for Wibeee config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.wibeee.const import (
    CONF_AUTO_CONFIGURE,
    CONF_MAC_ADDRESS,
    CONF_SCAN_INTERVAL,
    CONF_UPDATE_MODE,
    DOMAIN,
    MODE_LOCAL_PUSH,
    MODE_POLLING,
)

from .conftest import MOCK_DEVICE_INFO, MOCK_HOST, MOCK_MAC


# ---------------------------------------------------------------------------
# User step
# ---------------------------------------------------------------------------


async def test_user_step_shows_form(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test that the user step shows a form with host input."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert CONF_HOST in result["data_schema"].schema


async def test_user_step_validates_and_goes_to_mode(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_wibeee_api_config_flow,
) -> None:
    """Test user step validates device and moves to mode step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: MOCK_HOST},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "mode"


async def test_user_step_connection_error(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test user step shows error when device is unreachable."""
    with patch("custom_components.wibeee.config_flow.WibeeeAPI") as mock_cls:
        api = mock_cls.return_value
        api.async_check_connection = AsyncMock(return_value=False)

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.200"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_HOST: "no_device_info"}


async def test_user_step_already_configured(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_wibeee_api_config_flow,
) -> None:
    """Test that an already configured device is aborted."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_MAC,
        data={"host": MOCK_HOST, CONF_MAC_ADDRESS: MOCK_MAC},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: MOCK_HOST},
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


# ---------------------------------------------------------------------------
# Mode step
# ---------------------------------------------------------------------------


async def test_mode_step_local_push(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_wibeee_api_config_flow,
) -> None:
    """Test creating an entry with local push mode."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: MOCK_HOST},
    )
    assert result["step_id"] == "mode"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_UPDATE_MODE: MODE_LOCAL_PUSH, CONF_AUTO_CONFIGURE: False},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Wibeee {MOCK_DEVICE_INFO.mac_addr_short}"
    assert result["options"][CONF_UPDATE_MODE] == MODE_LOCAL_PUSH


async def test_mode_step_polling(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_wibeee_api_config_flow,
) -> None:
    """Test creating an entry with polling mode."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: MOCK_HOST},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_UPDATE_MODE: MODE_POLLING, CONF_AUTO_CONFIGURE: False},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_UPDATE_MODE] == MODE_POLLING
    assert CONF_SCAN_INTERVAL in result["options"]


async def test_mode_step_auto_configure_success(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_wibeee_api_config_flow,
) -> None:
    """Test auto-configure sends correct config to device."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: MOCK_HOST},
    )

    with (
        patch(
            "custom_components.wibeee.config_flow._get_local_ip",
            return_value="192.168.1.50",
        ),
        patch(
            "custom_components.wibeee.config_flow._get_ha_port",
            return_value=8123,
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_UPDATE_MODE: MODE_LOCAL_PUSH, CONF_AUTO_CONFIGURE: True},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    mock_wibeee_api_config_flow.async_configure_push_server.assert_called_once_with(
        "192.168.1.50", 8123
    )


async def test_mode_step_auto_configure_failure(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_wibeee_api_config_flow,
) -> None:
    """Test auto-configure failure shows error but allows retry."""
    mock_wibeee_api_config_flow.async_configure_push_server = AsyncMock(
        return_value=False
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: MOCK_HOST},
    )

    with (
        patch(
            "custom_components.wibeee.config_flow._get_local_ip",
            return_value="192.168.1.50",
        ),
        patch(
            "custom_components.wibeee.config_flow._get_ha_port",
            return_value=8123,
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_UPDATE_MODE: MODE_LOCAL_PUSH, CONF_AUTO_CONFIGURE: True},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "auto_configure_failed"}


# ---------------------------------------------------------------------------
# DHCP discovery
# ---------------------------------------------------------------------------


async def test_dhcp_discovery(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_wibeee_api_config_flow,
) -> None:
    """Test DHCP discovery triggers config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_DHCP},
        data=DhcpServiceInfo(
            ip=MOCK_HOST,
            macaddress="001ec0112233",
            hostname="wibeee",
        ),
    )
    # DHCP auto-fills and goes to user step with data, then to mode step
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "mode"


async def test_dhcp_discovery_already_configured(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test DHCP discovery aborts if device already configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_MAC,
        data={"host": MOCK_HOST, CONF_MAC_ADDRESS: MOCK_MAC},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_DHCP},
        data=DhcpServiceInfo(
            ip=MOCK_HOST,
            macaddress="001ec0112233",
            hostname="wibeee",
        ),
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_dhcp_discovery_not_wibeee(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test DHCP discovery aborts for non-Wibeee devices."""
    with patch("custom_components.wibeee.config_flow.WibeeeAPI") as mock_cls:
        api = mock_cls.return_value
        api.async_check_connection = AsyncMock(return_value=False)

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_DHCP},
            data=DhcpServiceInfo(
                ip="192.168.1.200",
                macaddress="001ec0aabbcc",
                hostname="unknown",
            ),
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "not_wibeee_device"


# ---------------------------------------------------------------------------
# Options flow
# ---------------------------------------------------------------------------


async def test_options_flow_switch_to_polling(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
) -> None:
    """Test switching from local push to polling via options flow."""
    mock_config_entry_push.add_to_hass(hass)

    # We need to set up the entry first so options flow works
    with patch("custom_components.wibeee.async_setup_entry", return_value=True):
        await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(
        mock_config_entry_push.entry_id
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_UPDATE_MODE: MODE_POLLING,
            CONF_SCAN_INTERVAL: 60,
            CONF_AUTO_CONFIGURE: False,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_UPDATE_MODE] == MODE_POLLING
    assert result["data"][CONF_SCAN_INTERVAL] == 60


async def test_options_flow_auto_configure(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api_config_flow,
) -> None:
    """Test auto-configure from options flow."""
    mock_config_entry_polling.add_to_hass(hass)

    with patch("custom_components.wibeee.async_setup_entry", return_value=True):
        await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
        await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(
        mock_config_entry_polling.entry_id
    )

    with (
        patch(
            "custom_components.wibeee.config_flow._get_local_ip",
            return_value="192.168.1.50",
        ),
        patch(
            "custom_components.wibeee.config_flow._get_ha_port",
            return_value=8123,
        ),
    ):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {
                CONF_UPDATE_MODE: MODE_LOCAL_PUSH,
                CONF_AUTO_CONFIGURE: True,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    mock_wibeee_api_config_flow.async_configure_push_server.assert_called_once_with(
        "192.168.1.50", 8123
    )
