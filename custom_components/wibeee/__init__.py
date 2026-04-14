"""
Wibeee Energy Monitor integration for Home Assistant.

This integration communicates with Wibeee (formerly Mirubee) energy monitoring
devices manufactured by Smilics/Circutor over the local network.

Supports two update modes:
- **Local Push** (default): The WiBeee pushes data to HA's built-in HTTP
  server (port 8123 by default) at ``/Wibeee/receiverAvg``.
  Can auto-configure the device to point to the HA instance.
- **Polling**: Periodically fetches status.xml from the device.

No HACS required - works as a native custom_component.

Documentation: https://github.com/fquinto/pywibeee
Device info: http://wibeee.circutor.com/
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_MAC_ADDRESS,
    CONF_UPDATE_MODE,
    DOMAIN,
    MODE_LOCAL_PUSH,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wibeee from a config entry."""
    mode = entry.options.get(CONF_UPDATE_MODE, MODE_LOCAL_PUSH)

    _LOGGER.info(
        "Setting up Wibeee config entry '%s' (unique_id=%s, mode=%s)",
        entry.title,
        entry.unique_id,
        mode,
    )

    # Store entry data in hass.data for use by platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # If local push mode, ensure the push receiver views are registered
    if mode == MODE_LOCAL_PUSH:
        from .push_receiver import async_setup_push_receiver

        async_setup_push_receiver(hass)

    # Reload on options change
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Forward setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(
        "Unloading Wibeee entry '%s' (unique_id=%s)",
        entry.title,
        entry.unique_id,
    )

    # If local push, unregister the device from the push receiver
    mode = entry.options.get(CONF_UPDATE_MODE, MODE_LOCAL_PUSH)
    if mode == MODE_LOCAL_PUSH:
        from .push_receiver import DATA_PUSH_RECEIVER

        mac_addr = entry.data.get(CONF_MAC_ADDRESS, "")
        if mac_addr:
            receiver = hass.data.get(DATA_PUSH_RECEIVER)
            if receiver is not None:
                receiver.unregister_device(mac_addr)

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )

    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        _LOGGER.info(
            "Unloaded Wibeee entry '%s' (unique_id=%s)",
            entry.title,
            entry.unique_id,
        )

    return unload_ok


async def async_update_options(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Handle options update - reload the entry."""
    await hass.config_entries.async_reload(entry.entry_id)
