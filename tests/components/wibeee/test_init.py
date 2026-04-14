"""Tests for Wibeee integration setup and unload."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.wibeee.const import (
    CONF_MAC_ADDRESS,
    CONF_UPDATE_MODE,
    CONF_WIBEEE_ID,
    DOMAIN,
    MODE_LOCAL_PUSH,
    MODE_POLLING,
)
from custom_components.wibeee.push_receiver import DATA_PUSH_RECEIVER

from .conftest import MOCK_HOST, MOCK_MAC


# ---------------------------------------------------------------------------
# Setup entry
# ---------------------------------------------------------------------------


async def test_setup_entry_local_push(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test setting up a local push entry."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry_push.state.name == "LOADED"
    assert DOMAIN in hass.data
    assert mock_config_entry_push.entry_id in hass.data[DOMAIN]

    # Push receiver should be registered
    assert DATA_PUSH_RECEIVER in hass.data


async def test_setup_entry_polling(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test setting up a polling entry."""
    mock_config_entry_polling.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry_polling.state.name == "LOADED"
    assert DOMAIN in hass.data


# ---------------------------------------------------------------------------
# Unload entry
# ---------------------------------------------------------------------------


async def test_unload_entry_local_push(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test unloading a local push entry."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry_push.state.name == "LOADED"

    await hass.config_entries.async_unload(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry_push.state.name == "NOT_LOADED"
    # Entry data should be cleaned up
    assert mock_config_entry_push.entry_id not in hass.data.get(DOMAIN, {})


async def test_unload_entry_polling(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test unloading a polling entry."""
    mock_config_entry_polling.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry_polling.state.name == "LOADED"

    await hass.config_entries.async_unload(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry_polling.state.name == "NOT_LOADED"


async def test_unload_push_no_mac_address(
    hass: HomeAssistant,
    mock_wibeee_api,
) -> None:
    """Test unloading push entry when MAC address is empty."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_MAC,
        title="Wibeee 2233",
        data={
            "host": MOCK_HOST,
            CONF_MAC_ADDRESS: "",  # Empty MAC
            CONF_WIBEEE_ID: "WIBEEE",
        },
        options={CONF_UPDATE_MODE: MODE_LOCAL_PUSH},
        version=2,
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Should unload without error even with empty MAC
    result = await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert result is True


async def test_unload_push_no_receiver(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test unloading push entry when push receiver was already removed."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    # Remove the push receiver before unload
    hass.data.pop(DATA_PUSH_RECEIVER, None)

    # Should unload without error
    result = await hass.config_entries.async_unload(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()
    assert result is True


# ---------------------------------------------------------------------------
# Options update triggers reload
# ---------------------------------------------------------------------------


async def test_options_update_reloads_entry(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
) -> None:
    """Test that changing options triggers a reload."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    with patch(
        "custom_components.wibeee.async_setup_entry", return_value=True
    ) as mock_setup:
        hass.config_entries.async_update_entry(
            mock_config_entry_push,
            options={CONF_UPDATE_MODE: MODE_POLLING},
        )
        await hass.async_block_till_done()

        # The entry should have been reloaded
        assert mock_setup.call_count >= 1
