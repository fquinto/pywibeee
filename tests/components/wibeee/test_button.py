"""Tests for Wibeee button platform."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.wibeee.const import DOMAIN

from .conftest import (
    MOCK_DEVICE_INFO,
    MOCK_HOST,
    MOCK_MAC,
    MOCK_SENSOR_DATA,
    MOCK_STATUS_XML,
)


@pytest.fixture
def mock_wibeee_api_button() -> Generator[MagicMock]:
    """Mock the WibeeeAPI class for button platform tests."""
    with patch(
        "custom_components.wibeee.button.WibeeeAPI", autospec=True
    ) as mock_cls:
        api = mock_cls.return_value
        api.async_check_connection = AsyncMock(return_value=True)
        api.async_fetch_device_info = AsyncMock(return_value=MOCK_DEVICE_INFO)
        api.async_fetch_sensors_data = AsyncMock(return_value=MOCK_SENSOR_DATA)
        api.async_fetch_status = AsyncMock(return_value=MOCK_STATUS_XML)
        api.async_configure_push_server = AsyncMock(return_value=True)
        api.async_reboot = AsyncMock(return_value=True)
        api.async_reset_energy = AsyncMock(return_value=True)
        api.host = MOCK_HOST
        yield api


# ---------------------------------------------------------------------------
# Button creation tests
# ---------------------------------------------------------------------------


async def test_buttons_created_push_mode(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
    mock_wibeee_api_button,
) -> None:
    """Test that button entities are created in push mode."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    states = hass.states.async_all("button")
    assert len(states) == 2

    entity_ids = [s.entity_id for s in states]
    assert any("reboot" in eid for eid in entity_ids), (
        f"No reboot button found in: {entity_ids}"
    )
    assert any("reset_energy" in eid for eid in entity_ids), (
        f"No reset energy button found in: {entity_ids}"
    )


async def test_buttons_created_polling_mode(
    hass: HomeAssistant,
    mock_config_entry_polling: MockConfigEntry,
    mock_wibeee_api,
    mock_wibeee_api_button,
) -> None:
    """Test that button entities are created in polling mode too."""
    mock_config_entry_polling.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_polling.entry_id)
    await hass.async_block_till_done()

    states = hass.states.async_all("button")
    assert len(states) == 2


# ---------------------------------------------------------------------------
# Button press tests
# ---------------------------------------------------------------------------


async def test_reboot_button_press(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
    mock_wibeee_api_button,
) -> None:
    """Test that pressing the reboot button calls async_reboot."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    # Find the reboot button entity
    states = hass.states.async_all("button")
    reboot_entity = next(
        (s for s in states if "reboot" in s.entity_id), None
    )
    assert reboot_entity is not None

    # Press the button
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": reboot_entity.entity_id},
        blocking=True,
    )

    mock_wibeee_api_button.async_reboot.assert_awaited_once()


async def test_reset_energy_button_press(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
    mock_wibeee_api_button,
) -> None:
    """Test that pressing the reset energy button calls async_reset_energy."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    # Find the reset energy button entity
    states = hass.states.async_all("button")
    reset_entity = next(
        (s for s in states if "reset_energy" in s.entity_id), None
    )
    assert reset_entity is not None

    # Press the button
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": reset_entity.entity_id},
        blocking=True,
    )

    mock_wibeee_api_button.async_reset_energy.assert_awaited_once()


# ---------------------------------------------------------------------------
# Button entity attributes tests
# ---------------------------------------------------------------------------


async def test_reboot_button_has_restart_device_class(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
    mock_wibeee_api_button,
) -> None:
    """Test that the reboot button has RESTART device class."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    states = hass.states.async_all("button")
    reboot_entity = next(
        (s for s in states if "reboot" in s.entity_id), None
    )
    assert reboot_entity is not None
    assert reboot_entity.attributes.get("device_class") == "restart"


async def test_buttons_entity_category_config(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
    mock_wibeee_api_button,
) -> None:
    """Test that buttons have entity_category CONFIG."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    button_states = hass.states.async_all("button")

    for state in button_states:
        entry = ent_reg.async_get(state.entity_id)
        assert entry is not None
        assert entry.entity_category == EntityCategory.CONFIG


async def test_buttons_on_main_device(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
    mock_wibeee_api_button,
) -> None:
    """Test that buttons are attached to the main device, not per-phase."""
    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    device_registry = dr.async_get(hass)
    ent_reg = er.async_get(hass)

    button_states = hass.states.async_all("button")
    for state in button_states:
        entry = ent_reg.async_get(state.entity_id)
        assert entry is not None
        assert entry.device_id is not None

        device = device_registry.async_get(entry.device_id)
        assert device is not None
        # Main device has identifier (DOMAIN, mac_addr) without phase suffix
        assert (DOMAIN, MOCK_MAC) in device.identifiers


async def test_reboot_button_failure_logged(
    hass: HomeAssistant,
    mock_config_entry_push: MockConfigEntry,
    mock_wibeee_api,
    mock_wibeee_api_button,
    caplog,
) -> None:
    """Test that a failed reboot is logged as error."""
    mock_wibeee_api_button.async_reboot = AsyncMock(return_value=False)

    mock_config_entry_push.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_push.entry_id)
    await hass.async_block_till_done()

    states = hass.states.async_all("button")
    reboot_entity = next(
        (s for s in states if "reboot" in s.entity_id), None
    )
    assert reboot_entity is not None

    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": reboot_entity.entity_id},
        blocking=True,
    )

    assert "failed" in caplog.text.lower() or "reboot" in caplog.text.lower()
