# Tests

## Automated test suite

119 tests covering the Home Assistant custom component and the pywibeee library.

Run all tests:

```sh
pytest tests/
```

### Test breakdown

| File | Tests | Coverage |
|------|------:|----------|
| `components/wibeee/test_api.py` | 40 | API client: XML parsing, HTTP errors, timeouts |
| `components/wibeee/test_push_receiver.py` | 16 | Push HTTP endpoint, parameter mapping, MAC routing |
| `components/wibeee/test_sensor.py` | 13 | Entity creation, availability, values, device info |
| `components/wibeee/test_coordinator.py` | 13 | Polling, push updates, error handling |
| `components/wibeee/test_config_flow.py` | 12 | User flow, DHCP discovery, options flow |
| `components/wibeee/test_button.py` | 8 | Reboot and reset energy buttons |
| `components/wibeee/test_init.py` | 6 | Setup, unload, runtime_data |
| `components/wibeee/test_const.py` | 5 | Sensor types, push mappings, model definitions |
| `test_project.py` | 3 | Package import, version, project metadata |

All tests are async (`asyncio_mode = "auto"`) and use `pytest-homeassistant-custom-component` fixtures.

---

## Manual CLI testing

```sh
./main.py --host 192.168.1.150 --get model -m request
./main.py --host 192.168.1.150 --get version -m request
./main.py --host 192.168.1.150 --get status -m request
./main.py --host 192.168.1.150 --get info -m request
./main.py --host 192.168.1.150 --get sensors -m request
./main.py --host 192.168.1.150 --get devicename -m request
./main.py --auto --get model -m request
./main.py --auto --get version -m request
./main.py --auto --get status -m request
./main.py --auto --get info -m request
./main.py --auto --get sensors -m request
./main.py --auto --get devicename -m request

./main.py --host 192.168.1.150 --get model -m async_aiohttp
./main.py --host 192.168.1.150 --get version -m async_aiohttp
./main.py --host 192.168.1.150 --get status -m async_aiohttp
./main.py --host 192.168.1.150 --get info -m async_aiohttp
./main.py --host 192.168.1.150 --get sensors -m async_aiohttp
./main.py --host 192.168.1.150 --get devicename -m async_aiohttp
./main.py --auto --get model -m async_aiohttp
./main.py --auto --get version -m async_aiohttp
./main.py --auto --get status -m async_aiohttp
./main.py --auto --get info -m async_aiohttp
./main.py --auto --get sensors -m async_aiohttp
./main.py --auto --get devicename -m async_aiohttp

./main.py --host 192.168.1.150 --get model -m async_httpx
./main.py --host 192.168.1.150 --get version -m async_httpx
./main.py --host 192.168.1.150 --get status -m async_httpx
./main.py --host 192.168.1.150 --get info -m async_httpx
./main.py --host 192.168.1.150 --get sensors -m async_httpx
./main.py --host 192.168.1.150 --get devicename -m async_httpx
./main.py --auto --get model -m async_httpx
./main.py --auto --get version -m async_httpx
./main.py --auto --get status -m async_httpx
./main.py --auto --get info -m async_httpx
./main.py --auto --get sensors -m async_httpx
./main.py --auto --get devicename -m async_httpx
```
