
pywibeee
========

.. image:: https://github.com/fquinto/pywibeee/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/fquinto/pywibeee/actions/workflows/tests.yml
   :alt: Tests

.. image:: https://img.shields.io/pypi/v/pywibeee.svg
   :target: https://pypi.org/project/pywibeee/
   :alt: PyPI version

Python library and CLI for WiBeee (old Mirubee) energy meters
manufactured by Smilics / Circutor.

.. contents:: Table of Contents
   :depth: 2

Home Assistant Integration
--------------------------

The official Home Assistant integration for WiBeee devices is built on top of
this library and has been proposed to Home Assistant core:

* Core pull request: https://github.com/home-assistant/core/pull/168419
* Documentation pull request: https://github.com/home-assistant/home-assistant.io/pull/44815

The integration is polling-only (``local_polling``, 30-second interval), with
config flow, DHCP discovery, and per-phase sensor entities. A development copy
of the integration lives in `ha_core_component/ <ha_core_component/>`_.

Python Library
--------------

Installation
~~~~~~~~~~~~

Install from PyPI (dependencies are installed automatically):

.. code-block:: sh

   pip install pywibeee --upgrade

Or install the latest source:

.. code-block:: sh

   pip install git+https://github.com/fquinto/pywibeee

Usage
~~~~~

The library exposes an async client, ``WibeeeAPI``, built on aiohttp:

.. code-block:: python

   import asyncio

   import aiohttp

   from pywibeee import WibeeeAPI


   async def main() -> None:
       async with aiohttp.ClientSession() as session:
           api = WibeeeAPI(session, "192.168.1.150")

           info = await api.async_fetch_device_info()
           print(info.model, info.mac_addr, info.firmware_version)

           data = await api.async_fetch_sensors_data()
           print(data["fase1"]["vrms"], data["fase4"]["p_activa"])


   asyncio.run(main())

Highlights:

* ``async_fetch_device_info()`` — model, MAC address, firmware version, and
  device ID. The whole discovery is bounded by an overall deadline (default
  15 seconds, ``deadline`` parameter) and raises ``TimeoutError`` when
  exceeded.
* ``async_fetch_sensors_data()`` — all sensor readings from ``status.xml``,
  organized per phase (``fase1``..``fase3``, ``fase4`` = total).
* ``async_check_connection()`` — quick check that the host is a WiBeee device.
* ``async_reboot()`` / ``async_reset_energy()`` — device actions.
* ``async_configure_push_server()`` / ``async_get_push_server_config()`` —
  configure or read the device's push destination.
* ``async_fetch_device_diagnostics()`` — configuration variables for
  diagnostics.
* Each HTTP request has a 10-second timeout (configurable) with optional
  retries; failed fetches are logged at debug level and return ``None``.

Tests
~~~~~

.. code-block:: sh

   pip install -e ".[test]"
   pytest

The suite covers XML parsing, HTTP errors, retries, the discovery deadline,
push server configuration, device actions, and diagnostics. It runs in CI on
Python 3.10, 3.12, and 3.14.

CLI
---

Command line interface for WiBeee (old Mirubee) meters.

Features
~~~~~~~~

* Autodiscover the host (IP) of the meter on the network.
* Get version, model, device name, info, status, and sensor list.
* Actions: reboot (via command or web), reset energy counters, configure push server.
* Output formats: xml, json, plain text, file.

Usage
~~~~~

.. code-block:: sh

   pywibeee -h

   usage: pywibeee [-h] [-version] (--host HOST | --auto) [-p PORT] [-t SETTIMEOUT]
                   [-o {xml,json,plain,file}]
                   (-a {reboot,rebootweb,resetenergy,configureserver} | -g {model,version,status,info,sensors,devicename})
                   [--serverip SERVERIP] [--serverport SERVERPORT]

   CLI for WiBeee (old Mirubee) meter

   optional arguments:
     -h, --help            show this help message and exit
     -version, --version   show program's version number and exit
     --host HOST           The host (or the IP) of the meter.
     --auto                Autodiscover host function, look IP on net.
     -p PORT, --port PORT  set port (default 80)
     -t SETTIMEOUT, --settimeout SETTIMEOUT
                           set timeout in seconds (default 10.0)
     -o FORMAT, --output FORMAT
                           xml|json|plain|file
     -a ACTION, --action ACTION
                           reboot|rebootweb|resetenergy|configureserver
     -g GET, --get GET     model|version|status|info|sensors|devicename
     --serverip SERVERIP   Server IP for push config (use with -a configureserver)
     --serverport SERVERPORT
                           Server port for push config (default 8600)

   Enjoy! :)

Examples
~~~~~~~~

Get status
^^^^^^^^^^

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 --get status
   {"response": {"model": "WBB", "webversion": "3.4.614", "time": "1570484447",
   "fase1_vrms": "228.70", "fase1_irms": "1.59", "fase1_p_activa": "264.34", ...}}

Get model
^^^^^^^^^

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 --get model
   {"response": {"model": "WBB", "model_description": "Wibeee BOX"}}

Get info
^^^^^^^^

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 -g info
   {"response": {"model": "WBB", "model_description": "Wibeee BOX",
   "webversion": "3.4.614", "host": "192.168.1.150", "devicename": "WIBEEE"}}

Get sensors with autodiscover
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

   $ pywibeee --auto -g sensors
   {"vrms": ["Vrms", "V", "mdi:sine-wave"], "irms": ["Irms", "A", "mdi:flash-auto"], ...}

Configure push server
^^^^^^^^^^^^^^^^^^^^^

Configure the WiBeee to push data to a server (e.g. ``192.168.1.50:8600``):

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 -a configureserver --serverip 192.168.1.50 --serverport 8600
   {"response": {"configureServer": "done (server=192.168.1.50:8600)"}}

The device will restart to apply the configuration. The port is sent in hexadecimal
to the WiBeee firmware (8600 decimal = ``2198`` hex).

Reboot the device
^^^^^^^^^^^^^^^^^

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 -a rebootweb

Reset energy counters
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 -a resetenergy


Local Push Protocol
-------------------

The WiBeee device can be configured to push data to a server via HTTP GET requests.
The device sends periodic requests to the configured server with all sensor values
as query parameters. The request path is hardcoded in the firmware; only the
destination host and port are configurable.

Endpoint
~~~~~~~~

.. code-block::

   GET /Wibeee/receiverAvg?mac=001ec0112233&v1=230.5&a1=277&e1=222157&vt=230.5&...

The server must respond with ``<<<WBAVG`` to acknowledge receipt.

The server can also send ``<<<WREBOOT`` to remotely reboot the device.

Push parameter mapping
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Push param prefix
     - Sensor
     - Unit
   * - ``v``
     - Phase voltage (vrms)
     - V
   * - ``i``
     - Current (irms)
     - A
   * - ``p``
     - Apparent power
     - VA
   * - ``a``
     - Active power
     - W
   * - ``r``
     - Inductive reactive power
     - var
   * - ``q``
     - Frequency
     - Hz
   * - ``f``
     - Power factor
     - —
   * - ``e``
     - Active energy
     - Wh
   * - ``o``
     - Inductive reactive energy
     - varh

Phase suffixes: ``1`` = L1, ``2`` = L2, ``3`` = L3, ``t`` = Total.

Example: ``v1`` = voltage L1, ``at`` = active power total, ``e2`` = active energy L2.

Configure push via HTTP
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

   # Set the push server (port in hex: 8123 = 1fbb for HA default port)
   curl "http://192.168.1.150/configura_server?ipServidor=192.168.1.50&URLServidor=192.168.1.50&portServidor=1fbb"

   # Reset the device to apply changes
   curl "http://192.168.1.150/config_value?reset=true"

Other useful HTTP endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

   # Harmonics data
   curl http://192.168.1.150/services/user/harmonics.xml

   # Waveform data (per phase)
   curl http://192.168.1.150/services/user/wafeformsF1.xml

   # Read measurement refresh rate
   curl "http://192.168.1.150/services/user/values.xml?var=WIBEEE.measuresRefresh"

   # Read app refresh rate
   curl "http://192.168.1.150/services/user/values.xml?var=WIBEEE.appRefresh"

   # Trigger WiFi scan and get results
   curl "http://192.168.1.150/scan.cgi?getAllBss"
   curl http://192.168.1.150/scanallresults.xml


Device Notes
------------

* Default IP: ``192.168.1.150``
* Default credentials:

  * Basic: ``user / user``
  * Admin: ``admin / Sm1l1cs?``
  * Admin (alt): ``admin / Wib333?``

* MAC OUI: ``00:1E:C0`` (Microchip Technology / Circutor)

Open ports
~~~~~~~~~~

.. code-block::

   80/tcp  open http      Web interface, configuration, bootloader commands
   502/tcp open modbus    Modbus TCP (input registers from 1009)
   550/tcp open binary    OTA firmware transfer (do NOT use without full understanding)

OTA commands
~~~~~~~~~~~~

* ``21001A 576246696E697368426F6F746C6F6164657250726F6363657373 0D0A`` (hex) = ``WbStartBootloaderProccess``
* ``200119 576246696e697368426f6f746c6f6164657250726f6363657373 0D0A`` (hex) = ``WbFinishBootloaderProccess``
* ``0D`` (hex) = Enter key = get version
* ``0F`` (hex) = read Backup Position
* ``01`` (hex) = reset

Models
~~~~~~

.. list-table::
   :header-rows: 1

   * - Code
     - Description
   * - WBM
     - Wibeee 1Ph
   * - WBT
     - Wibeee 3Ph
   * - WMX
     - Wibeee MAX
   * - WTD
     - Wibeee 3Ph RN
   * - WX2
     - Wibeee MAX 2S
   * - WX3
     - Wibeee MAX 3S
   * - WXX
     - Wibeee MAX MS
   * - WBB
     - Wibeee BOX
   * - WB3
     - Wibeee BOX S3P
   * - W3P
     - Wibeee 3Ph 3W
   * - WGD
     - Wibeee GND
   * - WBP
     - Wibeee SMART PLUG


Security
~~~~~~~~

The WiBeee has no authentication on local HTTP endpoints and uses plain HTTP.
Recommended precautions:

* Isolate the device on a separate VLAN or IoT network.
* Use firewall rules to restrict access to ports 80, 502, and 550.
* Do not expose the device to the internet.


Tools
-----

* Firmware files and downloader: `firmware/ <firmware/>`_
* WiBeee emulator: `emulator/ <emulator/>`_
* Cloud receiver server: `webserver/ <webserver/>`_


Changelog
---------

See `CHANGELOG.md <CHANGELOG.md>`_


License
-------

GNU General Public License version 2

* https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
* https://choosealicense.com/licenses/gpl-2.0/
* https://opensource.org/licenses/GPL-2.0


Donations for software development
----------------------------------

If this project is useful to you, you can support its development:

.. image:: https://img.shields.io/badge/Donate-PayPal-blue.svg
   :target: https://www.paypal.com/donate/?business=XQQJHGVPHLD7W&no_recurring=0&item_name=Thank+you+for+collaborating+and+helping+the+development+of+software+improvements.&currency_code=EUR
   :alt: Donate with PayPal

Thank you for collaborating and helping the development of software improvements.
