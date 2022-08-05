
pywibeee
========

Command line interface (CLI) for WiBeee (old Mirubee) meter.

Features
--------


* Autodiscover the host (IP) of the meter in a network
* Get version of the meter
* Get model of the meter
* Get info of the meter: (version + model + host)
* Get status meter data
* Get sensors of the meter
* Action: reset energy counter
* Action: reboot of the meter (via web or via special command)
* Several outputs when recieve data: xml, json, file, plain text
* 3 methods to get data: async_httpx, async_aiohttp, request

Requirements
------------

``pip install xmltodict requests aiohttp httpx``

Installation
------------

Install Python CLI package `pywibeee <https://pypi.org/project/pywibeee/>`_

``pip install pywibeee --upgrade``

Usage
-----

.. code-block:: sh

     pywibeee -h

     usage: pywibeee [-h] [-version] (--host HOST | --auto) [-t SETTIMEOUT]
                     [-o {xml,json,plain,file}]
                     [-p {80}]
                     [-m {async_httpx,async_aiohttp,request}]
                     (-a {reboot,rebootweb,resetenergy} | -g {model,version,status,info,sensors})

     CLI for WiBeee (old Mirubee) meter

     optional arguments:
       -h, --help            show this help message and exit
       -version, --version   show program's version number and exit
       --host HOST           The host (or the IP) of the meter.
       --auto                Autodiscover host function, look IP on net.
       -t SETTIMEOUT, --settimeout SETTIMEOUT
                             set timeout in seconds (default 10)
       -o {xml,json,plain,file}, --output {xml,json,plain,file}
                             xml|json|plain|file
       -a {reboot,rebootweb,resetenergy}, --action {reboot,rebootweb,resetenergy}
                             reboot|rebootweb|resetenergy
       -g {model,version,status,info,sensors}, --get {model,version,status,info,sensors}
                             model|version|status|info|sensors
       -p {portnumber}, --port {portnumber}
                             port number of the meter (default 80)
       -m {async_httpx, async_aiohttp, request}, --method {async_httpx, async_aiohttp, request}
                             async_httpx|async_aiohttp|request
                             (default async_httpx)

     Enjoy! :)

Use examples
^^^^^^^^^^^^

Get version
~~~~~~~~~~~

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 --get version
   {"response": {"webversion": "3.4.614"}}

Get model
~~~~~~~~~

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 --get model
   {"response": {"model": "WBB", "model_description": "Wibeee BOX"}}

Get info
~~~~~~~~

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 -g info
   {"response": {"model": "WBB", "model_description": "Wibeee BOX", "webversion": "3.4.614", "host": "192.168.1.150"}}

Get sensors with autodiscover
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sh

   $ pywibeee --auto -g sensors
   {"vrms": ["Vrms", "V", "mdi:power-plug"], "irms": ["Irms", "A", "mdi:flash-auto"], "p_aparent": ["Apparent Power", "VA", "mdi:flash-circle"], "p_activa": ["Active Power", "W", "mdi:flash"], "p_reactiva_ind": ["Inductive Reactive Power", "VArL", "mdi:flash-outline"], "p_reactiva_cap": ["Capacitive Reactive Power", "VArC", "mdi:flash-outline"], "frecuencia": ["Frequency", "Hz", "mdi:current-ac"], "factor_potencia": ["Power Factor", " ", "mdi:math-cos"], "energia_activa": ["Active Energy", "Wh", "mdi:pulse"], "energia_reactiva_ind": ["Inductive Reactive Energy", "VArLh", "mdi:alpha-e-circle-outline"], "energia_reactiva_cap": ["Capacitive Reactive Energy", "VArCh", "mdi:alpha-e-circle-outline"], "angle": ["Angle", "\u00b0", "mdi:angle-acute"], "thd_total": ["THD Current", "%", "mdi:chart-bubble"], "thd_fund": ["THD Current (fundamental)", "A", "mdi:vector-point"], "thd_ar3": ["THD Current Harmonic 3", "A", "mdi:numeric-3"], "thd_ar5": ["THD Current Harmonic 5", "A", "mdi:numeric-5"], "thd_ar7": ["THD Current Harmonic 7", "A", "mdi:numeric-7"], "thd_ar9": ["THD Current Harmonic 9", "A", "mdi:numeric-9"], "thd_tot_V": ["THD Voltage", "%", "mdi:chart-bubble"], "thd_fun_V": ["THD Voltage (fundamental)", "V", "mdi:vector-point"], "thd_ar3_V": ["THD Voltage Harmonic 3", "V", "mdi:numeric-3"], "thd_ar5_V": ["THD Voltage Harmonic 5", "V", "mdi:numeric-5"], "thd_ar7_V": ["THD Voltage Harmonic 7", "V", "mdi:numeric-7"], "thd_ar9_V": ["THD Voltage Harmonic 9", "V", "mdi:numeric-9"]}

Get status
~~~~~~~~~~

.. code-block:: sh

   $ pywibeee --host 192.168.1.150 --get status
   {"response": {"model": "WBB", "webversion": "3.4.614", "time": "1570484447", "fase1_vrms": "228.70", "fase1_irms": "1.59", "fase1_p_aparent": "362.65", "fase1_p_activa": "264.34", "fase1_p_reactiva_ind": "0.00", "fase1_p_reactiva_cap": "248.27", "fase1_frecuencia": "50.08", "fase1_factor_potencia": "-0.729", "fase1_energia_activa": "222157", "fase1_energia_reactiva_ind": "4631", "fase1_energia_reactiva_cap": "188269", "fase1_angle": "0.00", "fase1_thd_total": "64.60", "fase1_thd_fund": "1.40", "fase1_thd_ar3": "0.60", "fase1_thd_ar5": "0.50", "fase1_thd_ar7": "0.40", "fase1_thd_ar9": "0.40", "fase1_thd_tot_V": "0.00", "fase1_thd_fun_V": "228.50", "fase1_thd_ar3_V": "0.00", "fase1_thd_ar5_V": "0.00", "fase1_thd_ar7_V": "0.00", "fase1_thd_ar9_V": "0.00", "fase2_vrms": "228.70", "fase2_irms": "0.34", "fase2_p_aparent": "76.77", "fase2_p_activa": "50.99", "fase2_p_reactiva_ind": "0.00", "fase2_p_reactiva_cap": "0.00", "fase2_frecuencia": "50.08", "fase2_factor_potencia": "-0.664", "fase2_energia_activa": "47714", "fase2_energia_reactiva_ind": "5021", "fase2_energia_reactiva_cap": "641", "fase2_angle": "0.00", "fase2_thd_total": "0.00", "fase2_thd_fund": "0.00", "fase2_thd_ar3": "0.00", "fase2_thd_ar5": "0.00", "fase2_thd_ar7": "0.00", "fase2_thd_ar9": "0.00", "fase2_thd_tot_V": "0.00", "fase2_thd_fun_V": "228.50", "fase2_thd_ar3_V": "0.00", "fase2_thd_ar5_V": "0.00", "fase2_thd_ar7_V": "0.00", "fase2_thd_ar9_V": "0.00", "fase3_vrms": "228.70", "fase3_irms": "1.53", "fase3_p_aparent": "349.48", "fase3_p_activa": "265.40", "fase3_p_reactiva_ind": "0.00", "fase3_p_reactiva_cap": "227.37", "fase3_frecuencia": "50.08", "fase3_factor_potencia": "0.759", "fase3_energia_activa": "187069", "fase3_energia_reactiva_ind": "196", "fase3_energia_reactiva_cap": "159927", "fase3_angle": "0.00", "fase3_thd_total": "66.10", "fase3_thd_fund": "1.30", "fase3_thd_ar3": "0.60", "fase3_thd_ar5": "0.50", "fase3_thd_ar7": "0.40", "fase3_thd_ar9": "0.00", "fase3_thd_tot_V": "0.00", "fase3_thd_fun_V": "228.50", "fase3_thd_ar3_V": "0.00", "fase3_thd_ar5_V": "0.00", "fase3_thd_ar7_V": "0.00", "fase3_thd_ar9_V": "0.00", "fase4_vrms": "228.70", "fase4_irms": "3.45", "fase4_p_aparent": "788.90", "fase4_p_activa": "49.93", "fase4_p_reactiva_ind": "0.00", "fase4_p_reactiva_cap": "20.90", "fase4_frecuencia": "50.08", "fase4_factor_potencia": "-0.063", "fase4_energia_activa": "456941", "fase4_energia_reactiva_ind": "9849", "fase4_energia_reactiva_cap": "348839", "scale": "100", "coilStatus": null, "ground": "0.00", "model_description": "Wibeee BOX"}}

Notes
-----


* Default IP for WiBeee (old Mirubee): 192.168.1.150
* Default usernames / passwords:

  * Basic: ``user / user``
  * Admin: ``admin / Sm1l1cs?``
  * Admin another: ``admin / Wib333?``

* MAC Address: 00:1E:C0 (Microchip Technology)

OTA comands
^^^^^^^^^^^


* 21001A 576246696E697368426F6F746C6F6164657250726F6363657373 0D0A (hex) = ``WbStartBootloaderProccess`` = CHANGE_PORT_COMMAND_INIT
* 200119 576246696e697368426f6f746c6f6164657250726f6363657373 0D0A (hex) = ``WbFinishBootloaderProccess`` = CHANGE_PORT_COMMAND_FINAL
* 0D (hex) = Enter key = get version
* 0F (hex) = read Backup Position
* 01 (hex) = reset

Last firmware
^^^^^^^^^^^^^


* We have a folder with firmware on it: `firmware <firmware/>`_ and a `firmware finder downloader <firmware/download_check.py>`_

Tools for firmware and App investigation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Emulator of WiBeee product: `emulator <emulator/>`_
* Cloud server for WiBeee called webserver: `webserver <webserver/>`_

With this tools you can "play" with the firmware and the app.

Open ports
^^^^^^^^^^

.. code-block::

   80/tcp  open http      Microchip Libraries of Applications TCP/IP Stack httpd
   502/tcp open modbus    Modbus TCP
   550/tcp open new-rwho?

Models description WiBeee
-------------------------


* WBM = Wibeee 1Ph
* WBT = Wibeee 3Ph
* WMX = Wibeee MAX
* WTD = Wibeee 3Ph RN
* WX2 = Wibeee MAX 2S
* WX3 = Wibeee MAX 3S
* WXX = Wibeee MAX MS
* WBB = Wibeee BOX
* WB3 = Wibeee BOX S3P
* W3P = Wibeee 3Ph 3W
* WGD = Wibeee GND
* WBP = Wibeee SMART PLUG

Installation alternatives (getting latest source code)
------------------------------------------------------

  If you want to install latest source code:

  ``pip install git+http://github.com/fquinto/pywibeee``

  or

.. code-block:: sh

   git clone git://github.com/fquinto/pywibeee
   cd pywibeee
   python setup.py install

Changelog
---------


* See file CHANGELOG.md: `CHANGELOG.md <CHANGELOG.md>`_

Future development
------------------


* Improve another models.

License
-------

GNU General Public License version 2


* https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
* https://choosealicense.com/licenses/gpl-2.0/
* https://opensource.org/licenses/GPL-2.0
