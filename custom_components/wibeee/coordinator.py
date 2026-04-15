"""DataUpdateCoordinator for Wibeee energy monitors.

Handles both update modes:
- **Polling**: Periodically fetches status.xml (update_interval > 0).
- **Push**: Receives data via HTTP push (update_interval=None).
  Push data is injected via ``async_set_updated_data()``.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import WibeeeAPI

_LOGGER = logging.getLogger(__name__)

# Type alias: phase_key -> sensor_key -> value
WibeeeData = dict[str, dict[str, str]]


class WibeeeCoordinator(DataUpdateCoordinator[WibeeeData]):
    """Coordinator for Wibeee sensor data.

    In polling mode, ``_async_update_data`` fetches from the device API.
    In push mode, ``update_interval`` is None and data is injected
    externally via ``async_set_updated_data()``.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        api: WibeeeAPI,
        *,
        name: str = "Wibeee",
        update_interval: timedelta | None = None,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> WibeeeData:
        """Fetch data from the Wibeee device (polling mode only)."""
        try:
            data = await self.api.async_fetch_sensors_data(retries=2)
        except Exception as exc:
            raise UpdateFailed(
                f"Error fetching data from {self.api.host}: {exc}"
            ) from exc

        if data is None:
            raise UpdateFailed(f"No data received from Wibeee at {self.api.host}")
        return data
