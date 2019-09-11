# pywibeee

Command line interface (CLI) for WiBeee (old Mirubee) meter.

## Features

- Autodiscover the host (IP) of the meter in a network
- Get version of the meter
- Get model of the meter
- Get info of the meter: (version + model + host)
- Get status meter data
- Get sensors of the meter
- Action: reset energy counter
- Action: reboot of the meter (via web or via special command)
- Several outputs when recieve data: xml, json, file, plain text

## Requirements

`pip install jxmlease requests`

# Installation

Install Python CLI package [pywibeee](https://pypi.org/project/pywibeee/)

```
$ pip install pywibeee --upgrade
```

# Usage

```
$ pywibeee -h

usage: pywibeee [-h] [-version] (--host HOST | --auto) [-t SETTIMEOUT]
                [-o {xml,json,plain,file}]
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

Enjoy! :)
```

## Use examples

### Get version

```
$ python main.py --host 192.168.1.150 --get version
{'response': {'webversion': '3.4.614'}}
```

### Get model

```
$ python main.py --host 192.168.1.150 --get model
{'response': {'model': 'WBB'}}
```

### Get info

```
$ python main.py --autodiscover -g info
{'response': {'host': '192.168.1.150', 'model': 'WBB', 'webversion': '3.4.614'}}
```

### Get sensors

```
$ python main.py -a -g sensors
```

### Get status

```
$ python main.py --host 192.168.1.150 --get status
{'response': {'coilStatus': '',
              'fase1_angle': '0.00',
              'fase1_energia_activa': '1213',
              'fase1_energia_reactiva_cap': '969',
              'fase1_energia_reactiva_ind': '1',
              'fase1_factor_potencia': '-0.750',
              'fase1_frecuencia': '50.08',
              'fase1_irms': '1.70',
              'fase1_p_activa': '290.11',
              'fase1_p_aparent': '386.64',
              'fase1_p_reactiva_cap': '255.60',
              'fase1_p_reactiva_ind': '0.00',
              'fase1_thd_ar3': '0.60',
              'fase1_thd_ar3_V': '0.00',
              'fase1_thd_ar5': '0.50',
              'fase1_thd_ar5_V': '0.00',
              'fase1_thd_ar7': '0.40',
              'fase1_thd_ar7_V': '0.00',
              'fase1_thd_ar9': '0.30',
              'fase1_thd_ar9_V': '0.00',
              'fase1_thd_fun_V': '227.50',
              'fase1_thd_fund': '1.50',
              'fase1_thd_tot_V': '0.00',
              'fase1_thd_total': '61.60',
              'fase1_vrms': '227.48',
              'fase2_angle': '0.00',
              'fase2_energia_activa': '188',
              'fase2_energia_reactiva_cap': '0',
              'fase2_energia_reactiva_ind': '12',
              'fase2_factor_potencia': '-0.616',
              'fase2_frecuencia': '50.08',
              'fase2_irms': '0.36',
              'fase2_p_activa': '50.04',
              'fase2_p_aparent': '81.19',
              'fase2_p_reactiva_cap': '0.00',
              'fase2_p_reactiva_ind': '0.00',
              'fase2_thd_ar3': '0.00',
              'fase2_thd_ar3_V': '0.00',
              'fase2_thd_ar5': '0.00',
              'fase2_thd_ar5_V': '0.00',
              'fase2_thd_ar7': '0.00',
              'fase2_thd_ar7_V': '0.00',
              'fase2_thd_ar9': '0.00',
              'fase2_thd_ar9_V': '0.00',
              'fase2_thd_fun_V': '227.50',
              'fase2_thd_fund': '0.00',
              'fase2_thd_tot_V': '0.00',
              'fase2_thd_total': '0.00',
              'fase2_vrms': '227.48',
              'fase3_angle': '0.00',
              'fase3_energia_activa': '1179',
              'fase3_energia_reactiva_cap': '893',
              'fase3_energia_reactiva_ind': '0',
              'fase3_factor_potencia': '0.774',
              'fase3_frecuencia': '50.08',
              'fase3_irms': '1.64',
              'fase3_p_activa': '288.61',
              'fase3_p_aparent': '372.72',
              'fase3_p_reactiva_cap': '235.85',
              'fase3_p_reactiva_ind': '0.00',
              'fase3_thd_ar3': '0.60',
              'fase3_thd_ar3_V': '0.00',
              'fase3_thd_ar5': '0.50',
              'fase3_thd_ar5_V': '0.00',
              'fase3_thd_ar7': '0.40',
              'fase3_thd_ar7_V': '0.00',
              'fase3_thd_ar9': '0.30',
              'fase3_thd_ar9_V': '0.00',
              'fase3_thd_fun_V': '227.50',
              'fase3_thd_fund': '1.40',
              'fase3_thd_tot_V': '0.00',
              'fase3_thd_total': '66.80',
              'fase3_vrms': '227.48',
              'fase4_energia_activa': '2581',
              'fase4_energia_reactiva_cap': '1863',
              'fase4_energia_reactiva_ind': '14',
              'fase4_factor_potencia': '-0.061',
              'fase4_frecuencia': '50.08',
              'fase4_irms': '3.70',
              'fase4_p_activa': '51.54',
              'fase4_p_aparent': '840.55',
              'fase4_p_reactiva_cap': '19.75',
              'fase4_p_reactiva_ind': '0.00',
              'fase4_vrms': '227.48',
              'ground': '0.00',
              'model': 'WBB',
              'scale': '100',
              'time': '1567374124',
              'webversion': '3.4.614'}}
```

# Notes

- Default IP for WiBeee (old Mirubee): 192.168.1.150
- Default usernames / passwords:
    - Basic: `user / user`
    - Admin: `admin / Sm1l1cs?`
    - Admin another: `admin / Wib333?`
- OTA comands: WbStartBootloaderProccess, WbFinishBootloaderProccess
- Last (11/09/2019) OTA firmware file url: https://app.mirubee.com/api/fw/wbb/FOTAFile_V3.4.614_WBB.bin
    - MD5: 57d8c4a3c77e510fe0ae6ff44cdb7afc

# Models WiBeee

 - WBM = Wibeee 1Ph
 - WBT = Wibeee 3Ph
 - WMX = Wibeee MAX
 - WTD = Wibeee 3Ph RN
 - WX2 = Wibeee MAX 2S
 - WX3 = Wibeee MAX 3S
 - WXX = Wibeee MAX MS
 - WBB = Wibeee BOX
 - WB3 = Wibeee BOX S3P
 - W3P = Wibeee 3Ph 3W
 - WGD = Wibeee GND
 - WBP = Wibeee SMART PLUG

# Installation alternatives (getting latest source code)

If you want to install latest source code:

`$ pip install git+http://github.com/fquinto/pywibeee`

or

```
$ git clone git://github.com/fquinto/pywibeee
$ cd pywibeee
$ python setup.py install
```

# Changelog

- 0.0.1 First draft functional version.

# Future development

- Improve another models.

# Development CLI for Python references

- https://realpython.com/command-line-interfaces-python-argparse/


- `pip3 install --user pipenv`
- `pipenv install requests`
- `pipenv install jxmlease`

```
pipenv shell
pipenv run
```

## Generating distribution archives

- `python3 -m pip install --user --upgrade setuptools wheel`
- `python3 setup.py sdist bdist_wheel`
- `python setup.py sdist`
- `python -m pip install .`
- `python tests/test_project.py`

# License

GNU General Public License version 2

- https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
- https://choosealicense.com/licenses/gpl-2.0/
- https://opensource.org/licenses/GPL-2.0
