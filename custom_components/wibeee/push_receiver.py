"""
Local Push receiver for Wibeee energy monitors.

Runs an aiohttp web server on port 8600 that receives push data from
WiBeee devices. The device sends periodic GET requests to
/Wibeee/receiverAvg with all sensor values as query parameters.

This is a singleton server shared across all Wibeee config entries,
since all devices push to the same port.

Documentation: https://github.com/fquinto/pywibeee
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from urllib.parse import parse_qsl

from aiohttp import web
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import singleton

from .const import (
    DEFAULT_PUSH_PORT,
    PUSH_PARAM_TO_SENSOR,
    PUSH_PHASE_MAP,
)

_LOGGER = logging.getLogger(__name__)

# Type alias for push data callback
PushDataCallback = Callable[[dict[str, dict[str, str]]], None]


class PushReceiver:
    """Manages push data listeners for registered WiBeee devices.

    Each device is identified by its MAC address. When push data arrives,
    the receiver parses it and calls the registered callback.
    """

    def __init__(self) -> None:
        """Initialize the push receiver."""
        self._listeners: dict[str, PushDataCallback] = {}

    def register_device(
        self, mac_address: str, callback_fn: PushDataCallback
    ) -> None:
        """Register a device to receive push updates."""
        mac_clean = mac_address.replace(":", "").lower()
        self._listeners[mac_clean] = callback_fn
        _LOGGER.debug(
            "Registered push listener for MAC %s (total: %d)",
            mac_clean,
            len(self._listeners),
        )

    def unregister_device(self, mac_address: str) -> None:
        """Unregister a device from push updates."""
        mac_clean = mac_address.replace(":", "").lower()
        self._listeners.pop(mac_clean, None)
        _LOGGER.debug(
            "Unregistered push listener for MAC %s (remaining: %d)",
            mac_clean,
            len(self._listeners),
        )

    def get_listener(
        self, mac_address: str
    ) -> PushDataCallback | None:
        """Get the callback for a given MAC address."""
        mac_clean = mac_address.replace(":", "").lower()
        return self._listeners.get(mac_clean)


def parse_push_data(
    query_params: dict[str, str],
) -> dict[str, dict[str, str]]:
    """Parse push query parameters into organized phase/sensor data.

    Input: {"mac": "001ec0112232", "v1": "230.5", "a1": "277", "vt": "230.5", ...}
    Output: {
        "fase1": {"vrms": "230.5", "p_activa": "277", ...},
        "fase4": {"vrms": "230.5", ...},  # "t" suffix -> fase4 (total)
    }
    """
    phases: dict[str, dict[str, str]] = {}

    for param, value in query_params.items():
        if len(param) < 2:
            continue

        prefix = param[:-1]  # e.g. "v" from "v1"
        suffix = param[-1]  # e.g. "1" from "v1"

        # Check if this is a known sensor parameter
        sensor_key = PUSH_PARAM_TO_SENSOR.get(prefix)
        phase_key = PUSH_PHASE_MAP.get(suffix)

        if sensor_key and phase_key:
            if phase_key not in phases:
                phases[phase_key] = {}
            phases[phase_key][sensor_key] = value

    return phases


def create_push_app(receiver: PushReceiver) -> web.Application:
    """Create the aiohttp web application for receiving push data.

    Handles the following WiBeee push endpoints:
    - GET /Wibeee/receiverAvg  (main push endpoint)
    - GET /Wibeee/receiver     (alternative)
    - GET /Wibeee/receiverLeap (gradient data)
    """

    async def handle_push(request: web.Request) -> web.Response:
        """Handle incoming push data from a WiBeee device."""
        query = dict(parse_qsl(request.query_string))

        mac_addr = query.get("mac", "").replace(":", "").lower()
        if not mac_addr:
            _LOGGER.debug(
                "Received push data without MAC address: %s %s",
                request.method,
                request.path,
            )
            return web.Response(status=200, text="<<<WBAVG ")

        listener = receiver.get_listener(mac_addr)
        if listener is None:
            _LOGGER.debug(
                "Received push data from unregistered device %s, ignoring",
                mac_addr,
            )
            return web.Response(status=200, text="<<<WBAVG ")

        # Parse the push data into phase/sensor format
        parsed = parse_push_data(query)

        if parsed:
            _LOGGER.debug(
                "Received push data from %s: %d phases, %d values",
                mac_addr,
                len(parsed),
                sum(len(v) for v in parsed.values()),
            )
            listener(parsed)
        else:
            _LOGGER.debug(
                "Push data from %s contained no recognized sensors",
                mac_addr,
            )

        return web.Response(status=200, text="<<<WBAVG ")

    async def handle_receiver_leap(
        request: web.Request,
    ) -> web.Response:
        """Handle receiverLeap endpoint (gradient data)."""
        # Same parsing logic - the data format is the same
        query = dict(parse_qsl(request.query_string))
        mac_addr = query.get("mac", "").replace(":", "").lower()

        if mac_addr:
            listener = receiver.get_listener(mac_addr)
            if listener:
                parsed = parse_push_data(query)
                if parsed:
                    listener(parsed)

        return web.Response(status=200, text="<<<WGRADIENT=007 ")

    async def handle_unknown(request: web.Request) -> web.Response:
        """Handle unknown paths gracefully."""
        _LOGGER.debug(
            "Received unknown request: %s %s", request.method, request.path
        )
        return web.Response(status=200)

    app = web.Application()
    app.router.add_get("/Wibeee/receiverAvg", handle_push)
    app.router.add_get("/Wibeee/receiver", handle_push)
    app.router.add_get("/Wibeee/receiverLeap", handle_receiver_leap)
    app.router.add_route("*", "/{path:.*}", handle_unknown)

    return app


@singleton.singleton("wibeee_push_receiver")
async def async_get_push_receiver(
    hass: HomeAssistant,
    port: int = DEFAULT_PUSH_PORT,
) -> PushReceiver:
    """Get or create the singleton push receiver.

    The server is shared across all Wibeee config entries since all
    devices push to the same port. Uses HA's singleton pattern.

    Args:
        hass: Home Assistant instance.
        port: Port to listen on (default 8600).

    Returns:
        The PushReceiver instance.
    """
    receiver = PushReceiver()

    # Create the aiohttp app
    app = create_push_app(receiver)

    # Determine the local IP to bind to
    try:
        from homeassistant.components.network import async_get_source_ip
        from homeassistant.components.network.const import PUBLIC_TARGET_IP

        local_ip = await async_get_source_ip(hass, target_ip=PUBLIC_TARGET_IP)
    except Exception:
        local_ip = "0.0.0.0"

    # Start the web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, local_ip, port)
    await site.start()

    _LOGGER.info(
        "Wibeee push receiver listening on http://%s:%d", local_ip, port
    )

    @callback
    def shutdown_receiver(event: Event) -> None:
        """Shut down the push receiver on HA stop."""
        _LOGGER.info("Shutting down Wibeee push receiver")
        hass.async_create_task(runner.cleanup())

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, shutdown_receiver)

    return receiver
