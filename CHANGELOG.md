# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Integration 1.2.0 / Library 0.0.7 (2026)

### Added — Home Assistant Integration (`custom_components/wibeee/`)

* **Full Home Assistant custom integration** — install by copying `custom_components/wibeee/` to your HA `config/` directory. No HACS required.
* **Dual update mode**: choose between **Local Push** (default, recommended) and **Polling** during setup.
  * **Local Push**: the WiBeee pushes sensor data to HA in real time on port 8600. Lower latency, no polling overhead.
  * **Polling**: HA fetches `status.xml` from the device periodically (configurable interval, default 30 s).
* **Auto-configuration**: the integration can automatically configure the WiBeee device to push data to HA (sends the HA IP and port 8600 in hex to `/configura_server`, then resets the device).
* **DHCP auto-discovery**: devices with MAC prefix `00:1E:C0` (Circutor SA / Smilics) are detected automatically on the network.
* **Config Flow UI** with two steps: enter device IP (or confirm discovered IP) → choose update mode.
* **Options Flow**: switch between Local Push and Polling, change polling interval, or re-run auto-configuration at any time.
* **24 sensor types** per phase: voltage, current, active/apparent/reactive power, frequency, power factor, active energy, reactive energy (ind/cap), angle, THD current & voltage (total + fundamental + harmonics 3/5/7/9).
* **Device Registry**: proper device hierarchy — main device + per-phase sub-devices with manufacturer (Smilics), model, firmware version, and link to device web UI.
* **12 device models** supported: WBM, WBT, WMX, WTD, WX2, WX3, WXX, WBB, WB3, W3P, WGD, WBP.
* **Translations** in English, Spanish, and Catalan (config flow, options flow, entity names).
* **Entity translations** via `translation_key` and `SensorEntityDescription` — follows modern HA conventions.
* **HA unit constants**: `UnitOfElectricPotential.VOLT`, `UnitOfPower.WATT`, `UnitOfEnergy.WATT_HOUR`, etc. instead of hardcoded strings.
* **Push receiver**: singleton aiohttp server on port 8600, shared across multiple WiBeee entries. Parses `/Wibeee/receiverAvg`, `/Wibeee/receiver`, and `/Wibeee/receiverLeap` endpoints.
* Minimum HA version: 2024.1.0.

### Added — CLI Library (`pywibeee/`)

* New CLI action `configureserver` — configure the WiBeee to push data to a server:
  ```
  pywibeee --host 192.168.1.150 -a configureserver --serverip 192.168.1.50 --serverport 8600
  ```
* New methods `configureServer()` and `configureServerAsync()` — send push server configuration to the device (IP + port in hex) and reset.
* New CLI arguments `--serverip` and `--serverport` for the `configureserver` action.

### Changed — CLI Library (`pywibeee/`)

* Refactored `getModelDescription()` — replaced massive if/elif chain with `MODEL_DESCRIPTIONS` dictionary.
* Refactored `getSensors()` — replaced massive if/elif chain with `SENSOR_DEFINITIONS` dictionary.
* `asyncCall()` now supports `configureServer` action with `(server_ip, server_port)` tuple.
* Requires Python >= 3.10.
* Updated `pyproject.toml`: full project URLs, excludes `custom_components*` from PyPI package.

### Removed

* Removed broken `pywibeee/discovery.py` (imported non-existent module).

### Fixed

* Unified version string — single source of truth in `pywibeee/__init__.__version__`.

## 0.0.6 (5th August, 2022)

### Added

* Bug corrections and improvements

## 0.0.5 (30th July, 2022)

### Added

* Now we have 3 methods: async_httpx, async_aiohttp, request

## 0.0.4 (20th July, 2021) - (NEVER RELEASED)

### Added

* Adding asyncio functions and structure

## 0.0.3 (21st December, 2020) - (NEVER RELEASED)

### Added

* Adding port option. Default is 80.

## 0.0.2 (8th October, 2019)

### Changed

* Improve json output.
* Remove dependency jxmlease. New dependency xmltodict.
* Added model description.

## 0.0.1 (11th September, 2019)

### Added

* First draft functional version.
