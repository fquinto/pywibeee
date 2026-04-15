"""
Wibeee sensor platform for Home Assistant.

Creates sensor entities for each phase and sensor type detected on the
Wibeee energy monitor device. All sensors are ``CoordinatorEntity``
instances backed by a single ``WibeeeCoordinator``:

- **Polling mode**: Coordinator periodically fetches status.xml.
- **Push mode**: Coordinator receives data via ``async_set_updated_data()``.

Documentation: https://github.com/fquinto/pywibeee
"""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import WibeeeConfigEntry
from .api import WibeeeDeviceInfo
from .const import (
    DOMAIN,
    KNOWN_MODELS,
    SENSOR_TYPES,
    WibeeeSensorEntityDescription,
)
from .coordinator import WibeeeCoordinator

_LOGGER = logging.getLogger(__name__)

# Map phase names to human-readable labels
PHASE_NAMES: dict[str, str] = {
    "fase1": "L1",
    "fase2": "L2",
    "fase3": "L3",
    "fase4": "Total",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WibeeeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Wibeee sensor entities from a config entry."""
    runtime = entry.runtime_data
    coordinator = runtime.coordinator
    device_info = runtime.device_info

    # Wait for first data if not already available (polling first refresh)
    if coordinator.data is None:
        _LOGGER.warning(
            "No data available for Wibeee %s (%s); no sensors created",
            device_info.mac_addr_short,
            device_info.ip_addr,
        )
        return

    # Build entities from discovered phases/sensors.
    # Process fase4 (Total) first to ensure the parent device exists
    # before child phase devices that reference it via via_device.
    entities: list[WibeeeSensor] = []
    sorted_phases = sorted(
        coordinator.data.items(),
        key=lambda x: (0 if x[0] == "fase4" else 1, x[0]),
    )
    for phase_key, phase_data in sorted_phases:
        for sensor_key in phase_data:
            description = SENSOR_TYPES.get(sensor_key)
            if description is not None:
                entities.append(
                    WibeeeSensor(
                        coordinator=coordinator,
                        device_info=device_info,
                        phase_key=phase_key,
                        description=description,
                    )
                )

    if entities:
        async_add_entities(entities)
        _LOGGER.info(
            "Added %d sensors for Wibeee %s (%s)",
            len(entities),
            device_info.mac_addr_short,
            device_info.ip_addr,
        )
    else:
        _LOGGER.warning(
            "No sensors found for Wibeee %s (%s)",
            device_info.mac_addr_short,
            device_info.ip_addr,
        )


# ---------------------------------------------------------------------------
# Device info builder
# ---------------------------------------------------------------------------


def _build_device_info(device_info: WibeeeDeviceInfo, phase_key: str) -> DeviceInfo:
    """Build HA DeviceInfo for a sensor entity."""
    model_name = KNOWN_MODELS.get(device_info.model, f"Wibeee {device_info.model}")
    is_phase = phase_key in ("fase1", "fase2", "fase3")
    phase_label = PHASE_NAMES.get(phase_key, phase_key)

    if is_phase:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{device_info.mac_addr_formatted}_{phase_key}")},
            via_device=(DOMAIN, device_info.mac_addr_formatted),
            name=f"Wibeee {device_info.mac_addr_short} {phase_label}",
            model=f"{model_name} Clamp",
            manufacturer="Smilics",
        )
    return DeviceInfo(
        identifiers={(DOMAIN, device_info.mac_addr_formatted)},
        name=f"Wibeee {device_info.mac_addr_short}",
        model=model_name,
        manufacturer="Smilics",
        sw_version=device_info.firmware_version,
        configuration_url=f"http://{device_info.ip_addr}/",
    )


# ---------------------------------------------------------------------------
# Unified sensor entity (polling + push)
# ---------------------------------------------------------------------------


class WibeeeSensor(CoordinatorEntity[WibeeeCoordinator], SensorEntity):
    """Wibeee sensor entity backed by a coordinator.

    Works for both polling and push modes. The coordinator provides
    the data; the sensor reads its specific phase/key from it.
    """

    _attr_has_entity_name = True
    entity_description: WibeeeSensorEntityDescription

    def __init__(
        self,
        coordinator: WibeeeCoordinator,
        device_info: WibeeeDeviceInfo,
        phase_key: str,
        description: WibeeeSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._phase_key = phase_key
        self.entity_description = description

        self._attr_unique_id = (
            f"{device_info.mac_addr_formatted}_{phase_key}_{description.key}"
        )
        self._attr_translation_key = description.translation_key
        self._attr_device_info = _build_device_info(device_info, phase_key)

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        phase_data = self.coordinator.data.get(self._phase_key)
        if phase_data is None:
            return None
        value = phase_data.get(self.entity_description.key)
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @property
    def available(self) -> bool:
        """Return True if the coordinator has data for this sensor."""
        if not super().available:
            return False
        if self.coordinator.data is None:
            return False
        phase_data = self.coordinator.data.get(self._phase_key)
        if phase_data is None:
            return False
        return self.entity_description.key in phase_data
