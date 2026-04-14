"""Tests for Wibeee integration setup and unload."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.wibeee.const import (
    CONF_UPDATE_MODE,
    DOMAIN,
    MODE_LOCAL_PUSH,
    MODE_POLLING,
)
from custom_components.wibeee.push_receiver import DATA_PUSH_RECEIVER

from .conftest import MOCK_MAC


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
