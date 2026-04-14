"""
Wibeee button platform for Home Assistant.

Provides device-level action buttons:
- **Reboot Device**: Reboots the WiBeee via its web interface.
- **Reset Energy Counters**: Resets all accumulated energy counters to zero.

Both buttons are attached to the main device (Total), not per-phase.

Documentation: https://github.com/fquinto/pywibeee
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import WibeeeAPI, WibeeeDeviceInfo
from .const import (
    CONF_MAC_ADDRESS,
    CONF_WIBEEE_ID,
    DOMAIN,
    KNOWN_MODELS,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class WibeeeButtonEntityDescription(ButtonEntityDescription):
    """Describe a Wibeee button entity."""

    method: str  # Name of the WibeeeAPI async method to call


BUTTON_TYPES: tuple[WibeeeButtonEntityDescription, ...] = (
    WibeeeButtonEntityDescription(
        key="reboot",
        translation_key="reboot",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
        method="async_reboot",
    ),
    WibeeeButtonEntityDescription(
        key="reset_energy",
        translation_key="reset_energy",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:counter",
        method="async_reset_energy",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up Wibeee button entities from a config entry."""
    host = entry.data[CONF_HOST]
    mac_addr = entry.data[CONF_MAC_ADDRESS]
    wibeee_id = entry.data.get(CONF_WIBEEE_ID, "WIBEEE")

    session = async_get_clientsession(hass)
    api = WibeeeAPI(session, host)

    # Fetch device info for the device registry
    device_info = await api.async_fetch_device_info(retries=3)
    if device_info is None:
        _LOGGER.error("Could not get device info from %s for buttons", host)
        device_info = WibeeeDeviceInfo(
            wibeee_id=wibeee_id,
            mac_addr=mac_addr,
            model="Unknown",
            firmware_version="Unknown",
            ip_addr=host,
        )

    entities = [
        WibeeeButton(api=api, device_info=device_info, description=desc)
        for desc in BUTTON_TYPES
    ]

    async_add_entities(entities)
    _LOGGER.info(
        "Added %d button entities for Wibeee %s (%s)",
        len(entities),
        device_info.mac_addr_short,
        host,
    )
    return True


class WibeeeButton(ButtonEntity):
    """Wibeee button entity for device-level actions.

    Attached to the main device (Total/fase4), not per-phase.
    """

    _attr_has_entity_name = True
    entity_description: WibeeeButtonEntityDescription

    def __init__(
        self,
        api: WibeeeAPI,
        device_info: WibeeeDeviceInfo,
        description: WibeeeButtonEntityDescription,
    ) -> None:
        """Initialize the button entity."""
        self._api = api
        self.entity_description = description

        model_name = KNOWN_MODELS.get(
            device_info.model, f"Wibeee {device_info.model}"
        )

        self._attr_unique_id = (
            f"{device_info.mac_addr_formatted}_{description.key}"
        )
        self._attr_translation_key = description.translation_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_info.mac_addr_formatted)},
            name=f"Wibeee {device_info.mac_addr_short}",
            model=model_name,
            manufacturer="Smilics",
            sw_version=device_info.firmware_version,
            configuration_url=f"http://{device_info.ip_addr}/",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        method = getattr(self._api, self.entity_description.method)
        success = await method()
        if success:
            _LOGGER.info(
                "Wibeee %s: %s executed successfully",
                self._attr_unique_id,
                self.entity_description.key,
            )
        else:
            _LOGGER.error(
                "Wibeee %s: %s failed",
                self._attr_unique_id,
                self.entity_description.key,
            )
