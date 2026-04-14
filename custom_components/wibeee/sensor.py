"""
Wibeee sensor platform for Home Assistant.

Creates sensor entities for each phase and sensor type detected on the
Wibeee energy monitor device. Supports two update modes:

- **Polling mode**: Uses DataUpdateCoordinator to periodically fetch
  status.xml from the device.
- **Local Push mode**: Receives push data from the device via HTTP views
  registered on HA's built-in web server. Sensors update in real time.

Documentation: https://github.com/fquinto/pywibeee
"""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import WibeeeAPI, WibeeeDeviceInfo
from .const import (
    CONF_MAC_ADDRESS,
    CONF_SCAN_INTERVAL,
    CONF_UPDATE_MODE,
    CONF_WIBEEE_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    KNOWN_MODELS,
    MODE_LOCAL_PUSH,
    MODE_POLLING,
    SENSOR_TYPES,
    WibeeeSensorEntityDescription,
)

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
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up Wibeee sensor entities from a config entry."""
    host = entry.data[CONF_HOST]
    mac_addr = entry.data[CONF_MAC_ADDRESS]
    wibeee_id = entry.data.get(CONF_WIBEEE_ID, "WIBEEE")
    mode = entry.options.get(CONF_UPDATE_MODE, MODE_LOCAL_PUSH)

    session = async_get_clientsession(hass)
    api = WibeeeAPI(session, host)

    # Fetch device info for the device registry
    device_info = await api.async_fetch_device_info(retries=3)
    if device_info is None:
        _LOGGER.error("Could not get device info from %s", host)
        device_info = WibeeeDeviceInfo(
            wibeee_id=wibeee_id,
            mac_addr=mac_addr,
            model="Unknown",
            firmware_version="Unknown",
            ip_addr=host,
        )

    if mode == MODE_LOCAL_PUSH:
        await _setup_local_push(
            hass, entry, api, device_info, mac_addr, async_add_entities
        )
    else:
        await _setup_polling(
            hass, entry, api, device_info, async_add_entities
        )

    return True


async def _setup_polling(
    hass: HomeAssistant,
    entry: ConfigEntry,
    api: WibeeeAPI,
    device_info: WibeeeDeviceInfo,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors with polling mode using DataUpdateCoordinator."""
    scan_interval = timedelta(
        seconds=entry.options.get(
            CONF_SCAN_INTERVAL,
            int(DEFAULT_SCAN_INTERVAL.total_seconds()),
        )
    )

    coordinator = WibeeeDataCoordinator(
        hass, api, device_info, scan_interval
    )
    await coordinator.async_config_entry_first_refresh()

    entities: list[WibeeePollingSensor] = []
    if coordinator.data:
        # Process fase4 (Total) first to ensure the parent device exists
        # before child phase devices that reference it via via_device
        sorted_phases = sorted(
            coordinator.data.items(),
            key=lambda x: (0 if x[0] == "fase4" else 1, x[0]),
        )
        for phase_key, phase_data in sorted_phases:
            for sensor_key in phase_data:
                description = SENSOR_TYPES.get(sensor_key)
                if description is not None:
                    entities.append(
                        WibeeePollingSensor(
                            coordinator=coordinator,
                            device_info=device_info,
                            phase_key=phase_key,
                            description=description,
                        )
                    )

    if entities:
        async_add_entities(entities, True)
        _LOGGER.info(
            "Added %d polling sensors for Wibeee %s (%s)",
            len(entities),
            device_info.mac_addr_short,
            api.host,
        )


async def _setup_local_push(
    hass: HomeAssistant,
    entry: ConfigEntry,
    api: WibeeeAPI,
    device_info: WibeeeDeviceInfo,
    mac_addr: str,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors with local push mode.

    First does an initial poll to discover which sensors exist,
    then registers with the push receiver for real-time updates.
    """
    from .push_receiver import async_setup_push_receiver

    # Do one initial poll to discover available sensors
    initial_data = await api.async_fetch_sensors_data(retries=3)

    # Create entities based on discovered sensors
    entities: list[WibeeePushSensor] = []
    if initial_data:
        # Process fase4 (Total) first to ensure the parent device exists
        # before child phase devices that reference it via via_device
        sorted_phases = sorted(
            initial_data.items(),
            key=lambda x: (0 if x[0] == "fase4" else 1, x[0]),
        )
        for phase_key, phase_data in sorted_phases:
            for sensor_key in phase_data:
                description = SENSOR_TYPES.get(sensor_key)
                if description is not None:
                    entities.append(
                        WibeeePushSensor(
                            device_info=device_info,
                            phase_key=phase_key,
                            description=description,
                            initial_value=phase_data.get(sensor_key),
                        )
                    )

    if entities:
        async_add_entities(entities, True)
        _LOGGER.info(
            "Added %d push sensors for Wibeee %s (%s)",
            len(entities),
            device_info.mac_addr_short,
            api.host,
        )

        # Build a lookup for fast push updates
        entity_lookup: dict[str, dict[str, WibeeePushSensor]] = {}
        for entity in entities:
            phase = entity.phase_key
            sensor = entity.sensor_key
            if phase not in entity_lookup:
                entity_lookup[phase] = {}
            entity_lookup[phase][sensor] = entity

        # Register the push callback
        def on_push_data(
            data: dict[str, dict[str, str]],
        ) -> None:
            """Called when push data arrives from the device."""
            for push_phase_key, phase_data in data.items():
                phase_entities = entity_lookup.get(push_phase_key, {})
                for push_sensor_key, value in phase_data.items():
                    entity = phase_entities.get(push_sensor_key)
                    if entity is not None:
                        entity.update_from_push(value)

        receiver = async_setup_push_receiver(hass)
        receiver.register_device(mac_addr, on_push_data)

        # Unregister on entry unload
        def unregister() -> None:
            receiver.unregister_device(mac_addr)

        entry.async_on_unload(unregister)
    else:
        _LOGGER.warning(
            "No sensors found for Wibeee %s (%s). "
            "Initial poll returned no data.",
            device_info.mac_addr_short,
            api.host,
        )


# ---------------------------------------------------------------------------
# Data coordinator (polling mode)
# ---------------------------------------------------------------------------


class WibeeeDataCoordinator(DataUpdateCoordinator[dict[str, dict[str, str]]]):
    """Coordinator to manage fetching Wibeee data via polling."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: WibeeeAPI,
        device_info: WibeeeDeviceInfo,
        scan_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.device_info = device_info

        super().__init__(
            hass,
            _LOGGER,
            name=f"Wibeee {device_info.mac_addr_short}",
            update_interval=scan_interval,
        )

    async def _async_update_data(self) -> dict[str, dict[str, str]]:
        """Fetch data from the Wibeee device."""
        try:
            data = await self.api.async_fetch_sensors_data(retries=2)
            if data is None:
                raise UpdateFailed(
                    f"No data received from Wibeee at {self.api.host}"
                )
            return data
        except UpdateFailed:
            raise
        except Exception as exc:
            raise UpdateFailed(
                f"Error fetching data from {self.api.host}: {exc}"
            ) from exc


# ---------------------------------------------------------------------------
# Shared device info builder
# ---------------------------------------------------------------------------


def _build_device_info(
    device_info: WibeeeDeviceInfo, phase_key: str
) -> DeviceInfo:
    """Build HA DeviceInfo for a sensor entity."""
    model_name = KNOWN_MODELS.get(
        device_info.model, f"Wibeee {device_info.model}"
    )
    is_phase = phase_key in ("fase1", "fase2", "fase3")
    phase_label = PHASE_NAMES.get(phase_key, phase_key)

    if is_phase:
        return DeviceInfo(
            identifiers={
                (DOMAIN, f"{device_info.mac_addr_formatted}_{phase_key}")
            },
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


def _build_unique_id(
    device_info: WibeeeDeviceInfo, phase_key: str, sensor_key: str
) -> str:
    """Build unique_id for a sensor entity."""
    return f"{device_info.mac_addr_formatted}_{phase_key}_{sensor_key}"


# ---------------------------------------------------------------------------
# Polling sensor entity
# ---------------------------------------------------------------------------


class WibeeePollingSensor(
    CoordinatorEntity[WibeeeDataCoordinator], SensorEntity
):
    """Wibeee sensor updated via polling (DataUpdateCoordinator)."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: WibeeeSensorEntityDescription

    def __init__(
        self,
        coordinator: WibeeeDataCoordinator,
        device_info: WibeeeDeviceInfo,
        phase_key: str,
        description: WibeeeSensorEntityDescription,
    ) -> None:
        """Initialize the polling sensor."""
        super().__init__(coordinator)

        self._phase_key = phase_key
        self.entity_description = description

        self._attr_unique_id = _build_unique_id(
            device_info, phase_key, description.key
        )
        self._attr_translation_key = description.translation_key
        self._attr_device_info = _build_device_info(device_info, phase_key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

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
        """Return True if the sensor has data."""
        if not super().available:
            return False
        if self.coordinator.data is None:
            return False
        phase_data = self.coordinator.data.get(self._phase_key)
        if phase_data is None:
            return False
        return self.entity_description.key in phase_data


# ---------------------------------------------------------------------------
# Push sensor entity
# ---------------------------------------------------------------------------


class WibeeePushSensor(SensorEntity):
    """Wibeee sensor updated via Local Push from the device.

    The device sends data to /Wibeee/receiverAvg on HA's HTTP server.
    Values are pushed in real time (typically every few seconds).
    """

    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: WibeeeSensorEntityDescription

    def __init__(
        self,
        device_info: WibeeeDeviceInfo,
        phase_key: str,
        description: WibeeeSensorEntityDescription,
        initial_value: str | None = None,
    ) -> None:
        """Initialize the push sensor."""
        self._phase_key = phase_key
        self._push_value: str | None = initial_value
        self._attr_available = initial_value is not None
        self.entity_description = description

        self._attr_unique_id = _build_unique_id(
            device_info, phase_key, description.key
        )
        self._attr_translation_key = description.translation_key
        self._attr_device_info = _build_device_info(device_info, phase_key)

    @property
    def phase_key(self) -> str:
        """Return the phase key for push lookup."""
        return self._phase_key

    @property
    def sensor_key(self) -> str:
        """Return the sensor key for push lookup."""
        return self.entity_description.key

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self._push_value is None:
            return None
        try:
            return float(self._push_value)
        except (ValueError, TypeError):
            return None

    @callback
    def update_from_push(self, value: str) -> None:
        """Update the sensor value from push data.

        Called by the push receiver when new data arrives.
        """
        self._push_value = value
        self._attr_available = True
        if self.hass:
            self.async_write_ha_state()
