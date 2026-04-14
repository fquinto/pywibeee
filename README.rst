
pywibeee
========

Python library, CLI, and Home Assistant integration for WiBeee (old Mirubee) energy meters
manufactured by Smilics / Circutor.

.. contents:: Table of Contents
   :depth: 2

Home Assistant Integration
--------------------------

Native custom component for Home Assistant. No HACS required.

Supports two update modes (user chooses during setup):

* **Local Push** (default, recommended) — the WiBeee sends data to HA's HTTP server in real time. Lowest latency.
* **Polling** — HA periodically fetches ``status.xml`` from the device (configurable interval, default 30 s).

Features
~~~~~~~~

* Config Flow UI — add the device from the HA interface.
* DHCP auto-discovery — devices with MAC prefix ``00:1E:C0`` are detected automatically.
* Auto-configuration — the integration can configure the WiBeee to push data to HA (IP + HTTP port).
* 24 sensor types per phase: voltage, current, active/apparent/reactive power, frequency, power factor, active energy, reactive energy, angle, THD current & voltage with harmonics.
* Device Registry with manufacturer, model, firmware version, and link to the device web UI.
* Options Flow — switch modes, change polling interval, or re-run auto-configuration at any time.
* Translations: English, Spanish, Catalan.
* 12 device models: WBM, WBT, WMX, WTD, WX2, WX3, WXX, WBB, WB3, W3P, WGD, WBP.

Installation
~~~~~~~~~~~~

Copy the ``custom_components/wibeee/`` folder into your Home Assistant ``config/custom_components/`` directory:

.. code-block:: sh

   # From the repository root
   cp -r custom_components/wibeee /path/to/ha/config/custom_components/

Restart Home Assistant, then go to **Settings → Devices & Services → Add Integration → Wibeee Energy Monitor**.

The integration will ask for:

1. The device IP address (or it will be pre-filled if discovered via DHCP).
2. The update mode: **Local Push** (recommended) or **Polling**.

If you choose Local Push with auto-configure enabled, the integration sends the HA IP and port to the WiBeee device and restarts it. The device will start pushing data to HA immediately.

Requirements
~~~~~~~~~~~~

* Home Assistant 2025.1.0 or later.
* WiBeee device accessible on the local network (static IP or DHCP reservation recommended).
* For Local Push: the WiBeee must be able to reach HA's HTTP port (8123 by default).


CLI Library
-----------

Command line interface for WiBeee (old Mirubee) meters.

Features
~~~~~~~~

* Autodiscover the host (IP) of the meter on the network.
* Get version, model, device name, info, status, and sensor list.
* Actions: reboot (via command or web), reset energy counters, configure push server.
* Output formats: xml, json, plain text, file.
* Uses ``httpx`` for both sync and async HTTP calls (no other HTTP dependencies).

Requirements
~~~~~~~~~~~~

.. code-block:: sh

   pip install xmltodict httpx

Installation
~~~~~~~~~~~~

Install from PyPI:

.. code-block:: sh

   pip install pywibeee --upgrade

Or install latest source:

.. code-block:: sh

   pip install git+https://github.com/fquinto/pywibeee

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

Configure the WiBeee to push data to a server (e.g. Home Assistant on ``192.168.1.50:8600``):

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
as query parameters.

Endpoint
~~~~~~~~

.. code-block::

   GET /Wibeee/receiverAvg?mac=001ec0112233&v1=230.5&a1=277&e1=222157&vt=230.5&...

The server must respond with ``<<<WBAVG`` to acknowledge receipt.

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

   80/tcp  open http      Microchip Libraries of Applications TCP/IP Stack httpd
   502/tcp open modbus    Modbus TCP
   550/tcp open new-rwho?

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


Community
---------

Join the Telegram community channel for support, questions, and discussion:

* https://t.me/wibeee_community
