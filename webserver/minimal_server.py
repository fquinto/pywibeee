#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR    | DATE       | VERSION | COMMENTS
# F.Quinto  | 2021-07-20 | 0.0.0   | First draft

__version__ = "0.0.0"
"""FastAPI using upgrader."""

from fastapi import FastAPI, Query, Depends, Request, Response
from pydantic import BaseModel
import uvicorn
import time


class Wibeee(BaseModel):
    mac:str = Query(None, max_length=12)
    ip:str = Query(None, max_length=15)
    soft:str = Query(None, max_length=20)
    model:str = Query(None, max_length=20)
    time:str = Query(0)
    v1:str = Query(0)  # vrms1 Tensión fase L1 (V)
    v2:str = Query(0)  # vrms2 Tensión fase L2 (V)
    v3:str = Query(0)  # vrms3 Tensión fase L3 (V)
    vt:str = Query(0)  # vrmst Tensión total (promedio L1, L2, L3) (V)
    i1:str = Query(0)  # irms1 Corriente L1 (A)
    i2:str = Query(0)  # irms2 Corriente L2 (A)
    i3:str = Query(0)  # irms3 Corriente L3 (A)
    it:str = Query(0)  # irmst Corriente total (promedio L1, L2, L3) (A)
    p1:str = Query(0)  # pap1 Potencia Aparente L1 (VA)
    p2:str = Query(0)  # pap2 Potencia Aparente L2 (VA)
    p3:str = Query(0)  # pap3 Potencia Aparente L3 (VA)
    pt:str = Query(0)  # papt Potencia Aparente Total (VA)
    a1:str = Query(0)  # pac1 Potencia Activa L1 (W)
    a2:str = Query(0)  # pac2 Potencia Activa L2 (W)
    a3:str = Query(0)  # pac3 Potencia Activa L3 (W)
    at:str = Query(0)  # pact Potencia Activa Total (W)
    r1:str = Query(0)  # preac1 Potencia Reactiva L1 (Var)
    r2:str = Query(0)  # preac2 Potencia Reactiva L2 (Var)
    r3:str = Query(0)  # preac3 Potencia Reactiva L3 (Var)
    rt:str = Query(0)  # preact Potencia Reactiva Total (Var)
    q1:str = Query(0)  # freq1 Frecuencia L1 (Hz)
    q2:str = Query(0)  # freq2 Frecuencia L2 (Hz)
    q3:str = Query(0)  # freq3 Frecuencia L3 (Hz)
    qt:str = Query(0)  # freqt Frecuencia total (promedio L1, L2, L3) (Hz)
    f1:str = Query(0)  # fpot1 Factor de potencia L1 (-)
    f2:str = Query(0)  # fpot2 Factor de potencia L2 (-)
    f3:str = Query(0)  # fpot3 Factor de potencia L3 (-)
    ft:str = Query(0)  # fpott Factor de potencia Total (-)
    e1:str = Query(0)  # eac1 Energía activa L1 (Wh)
    e2:str = Query(0)  # eac2 Energía activa L2 (Wh)
    e3:str = Query(0)  # eac3 Energía activa L3 (Wh)
    et:str = Query(0)  # eactt Energía activa Total (Wh)
    o1:str = Query(0)  # ereactl1 Energía reactiva inductiva L1 (VArLh)
    o2:str = Query(0)  # ereactl2 Energía reactiva inductiva L2 (VArLh)
    o3:str = Query(0)  # ereactl3 Energía reactiva inductiva L3 (VArLh)
    ot:str = Query(0)  # ereactlt Energía reactiva inductiva Total (VArLh)
                       # ereactc1 Energía reactiva capacitiva L1 (VArCh)
                       # ereactc2 Energía reactiva capacitiva L2 (VArCh)
                       # ereactc3 Energía reactiva capacitiva L3 (VArCh)
                       # ereactct Energía reactiva capacitiva total (VArCh)
    t1t:str = Query(0)  # fase1_thd_total (%)
    t11:str = Query(0)  # fase1_thd_fund (A)
    t13:str = Query(0)  # fase1_thd_ar3 (A)
    t15:str = Query(0)  # fase1_thd_ar5 (A)
    t17:str = Query(0)  # fase1_thd_ar7 (A)
    t19:str = Query(0)  # fase1_thd_ar9 (A)
    t2t:str = Query(0)  # fase2_thd_total (%)
    t21:str = Query(0)  # fase2_thd_fund (A)
    t23:str = Query(0)  # fase2_thd_ar3 (A)
    t25:str = Query(0)  # fase2_thd_ar5 (A)
    t27:str = Query(0)  # fase2_thd_ar7 (A)
    t29:str = Query(0)  # fase2_thd_ar9 (A)
    t3t:str = Query(0)  # fase3_thd_total (%)
    t31:str = Query(0)  # fase3_thd_fund (A)
    t33:str = Query(0)  # fase3_thd_ar3 (A)
    t35:str = Query(0)  # fase3_thd_ar5 (A)
    t37:str = Query(0)  # fase3_thd_ar7 (A)
    t39:str = Query(0)  # fase3_thd_ar9 (A)

nombre = 'WIBEEE'
mac = '00:1e:c0:11:22:33'
model = 'WBB'
version = '3.4.634'
serverdata = 'wattius.mirubee.com'
portdata = '8600'
device = {
    'phasesSequence': '123',
    'phases_sequence': '123',
    'model': model,
    'version': version,
    'nombre': nombre,
    'mac': mac,
    'macAddr': mac
}
primeravez = True
app = FastAPI()


# sudo -H pip install -r requirements.txt
# sudo -H pip install uvicorn --upgrade
# INFO:     192.168.1.69:38870 - "GET /scan.cgi?scan=1 HTTP/1.1" 404 Not Found
# sudo apt install httpie
# http -v http://192.168.1.150/scan.cgi?scan=1
# http -v http://192.168.1.150/scan.cgi?getAllBss
# http -v http://192.168.1.150/en/login.html
# NOOOO: http -v -f POST http://192.168.1.150/loginRedirect.html user=user pwd=user
# http -v http://192.168.1.150/en/loginRedirect.html?user=user&pwd=user
# /en/login.html?error=1
# http -v http://192.168.1.150/en/index.html
# http -v http://192.168.1.150/config_value?softaprescan=true
# 
# http -v http://192.168.1.150/scanallresults.xml

# Mi conexión:
# http -v http://192.168.1.150/scanresult.xml

# ERROR unable to resolve wibeee.smilics.com: no address associated with hostname
# http -v http://192.168.1.150/services/user/devices.xml

# http -v http://192.168.1.150/config_value?phases_sequence=123
# http -v http://192.168.1.150/services/user/values.xml?var=WIBEEE.phasesSequence

# http -v http://192.168.1.150/configura_server?URLServidor=wattius.mirubee.com&portServidor=1f90
# http -v http://192.168.1.150/configura_server?URLServidor=192.168.1.222&portServidor=1f90

# http -v http://192.168.1.150/services/user/values.xml?var=WIBEEE.model
# http -v http://192.168.1.150/services/user/values.xml?var=WIBEEE.macAddr

# http -v http://192.168.1.150/config_value?name=WIBEEE&dhcp=true&ip=c0a80196&gw=c0a80101&subnet=ffff0000
# http -v http://192.168.1.150/config_value?ssid=yourwifinetwork&security=5&typekey=2
# http -v http://192.168.1.150/config_value?pass=12345678
# http -v http://192.168.1.150/configura_server?URLServidor=wattius.mirubee.com&portServidor=1f90
# http -v http://192.168.1.150/config_value?reset=true

# Todas las variables
# http -v http://192.168.1.150/services/user/values.xml?id=WIBEEE

# http -v http://192.168.1.150/scan.cgi
# http -v http://192.168.1.150/changeScale?changeScale=1&low=1&id=724


def hexval2ip(valor):
    """From hex value to ip."""
    import socket
    import struct
    # Example
    # valor = 'c0a80196'
    addr_long = int(valor, 16)
    ip = socket.inet_ntoa(struct.pack(">L", addr_long))
    # ip = '.'.join(map(str, [int(valor[i:i+2], 16) for i in range(0, len(valor), 2)]))
    return ip


def hexval2decval(valor):
    """From hex value to port."""
    # Example: '2198' => '8600'
    port = int(valor, 16)
    return str(port)


def decval2hexval(valor):
    """From dec value to hex value (port)."""
    # Example: '8600' => '2198'
    port = int(valor)
    # return hex(port)
    return format(port, 'x')


def ip2hex(ip):
    """From ip to hex value."""
    # Example: '192.168.1.1' => 'c0a80101'
    ipfinal = ''.join([hex(int(x)+256)[3:] for x in ip.split('.')])
    return ipfinal


@app.get("/configura_server")
async def configura_server(request: Request):
    print('configura_server')
    data = ''
    time.sleep(0.3)
    params = str(request.query_params)
    print(params)
    print(str(request.headers))
    headers = {
        "Cache-Control": 'max-age=600',
        "Connection": 'close',
    }
    return Response(headers=headers, content=data)


# http -v http://192.168.1.150/changeScale?changeScale=1&low=1&id=724
@app.get("/changeScale")
async def changeScale(request: Request):
    print('changeScale')
    data = ''
    time.sleep(0.3)
    params = str(request.query_params)
    print(params)
    print(str(request.headers))
    headers = {
        "Cache-Control": 'max-age=600',
        "Connection": 'close',
    }
    return Response(headers=headers, content=data)


@app.get("/config_value")
async def config_value(request: Request):
    global device
    print('config_value')
    data = ''
    for param in request.query_params:
        helper = ''
        var = param
        value = request.query_params[param]
        device[var] = value
        if var == 'ip':
            helper = hexval2ip(value)
        elif var == 'portServidor':
            helper = hexval2decval(value)
        print(var, value, helper)
    params = str(request.query_params)
    # print(params)
    print(str(request.headers))
    headers = {
        "Cache-Control": 'max-age=600',
        "Connection": 'close',
    }
    time.sleep(0.3)
    print(device)
    return Response(headers=headers, content=data)


# Get data from variables (ask for data)
@app.get("/services/user/values.xml")
async def services_values(request: Request):
    import random
    global mac
    global nombre
    global model
    global version
    global serverdata
    global portdata
    global device
    print('values.xml')
    params = str(request.query_params)
    xmlheader = '<?xml version="1.0" encoding="UTF-8"?>\n\n'
    if 'var' in request.query_params:
        var = request.query_params['var']
        aux = var.split('.')
        var = aux[1]
        if var in device:
            value = device[var]
        else:
            value = round(random.uniform(3.0, 4.0), 2)
        if var == 'model':
            value = model
        elif var == 'macAddr':
            value = mac
        print(f'var:{var}    value:{value}')
        valuesxml = f'<values><variable><id>{var}</id><value>{value}</value></variable></values>'
    elif 'id' in request.query_params:
        idvar = request.query_params['id']
        if idvar == nombre:
            valuesxml = (
                '<values>'
                '<variable><id>measuresRefresh</id><value>60</value></variable>'
                '<variable><id>appRefresh</id><value>1</value></variable>'
                '<variable><id>HDataSaveRefresh</id><value>1</value></variable>'
                '<variable><id>connectionType</id><value>1</value></variable>'
                '<variable><id>phasesSequence</id><value>0</value></variable>'
                '<variable><id>harmonics</id><value>1</value></variable>'
                f'<variable><id>softVersion</id><value>{version}</value></variable>'
                f'<variable><id>model</id><value>{model}</value></variable>'
                '<variable><id>ipType</id><value>1</value></variable>'
                '<variable><id>ipAddr</id><value>192.168.1.150</value></variable>'
                '<variable><id>gwAddr</id><value>192.168.1.1</value></variable>'
                '<variable><id>subnetMask</id><value>255.255.0.0</value></variable>'
                '<variable><id>primaryDNS</id><value>8.8.8.8</value></variable>'
                '<variable><id>secondaryDNS</id><value>8.8.4.4</value></variable>'
                f'<variable><id>macAddr</id><value>{mac}</value></variable>'
                '<variable><id>ssid</id><value>yourwifinetwork</value></variable>'
                '<variable><id>keyEnc</id><value>0</value></variable>'
                '<variable><id>keyType</id><value>1</value></variable>'
                '<variable><id>securKey</id><value>12345678</value></variable>'
                f'<variable><id>serverIp</id><value>{serverdata}</value></variable>'
                '<variable><id>serverIpResolved</id><value></value></variable>'
                f'<variable><id>serverPort</id><value>{portdata}</value></variable>'
                '<variable><id>networkType</id><value>4</value></variable>'
                '<variable><id>spiFlashId</id><value>8</value></variable>'
                '<variable><id>leapThreshold</id><value>5</value></variable>'
                '<variable><id>clampsModel</id><value>-</value></variable>'
                '<variable><id>vrms1</id><value>224.75</value></variable>'
                '<variable><id>vrms2</id><value>224.75</value></variable>'
                '<variable><id>vrms3</id><value>224.75</value></variable>'
                '<variable><id>vrmst</id><value>224.75</value></variable>'
                '<variable><id>irms1</id><value>0.00</value></variable>'
                '<variable><id>irms2</id><value>0.17</value></variable>'
                '<variable><id>irms3</id><value>0.22</value></variable>'
                '<variable><id>irmst</id><value>0.39</value></variable>'
                '<variable><id>pap1</id><value>0.00</value></variable>'
                '<variable><id>pap2</id><value>38.85</value></variable>'
                '<variable><id>pap3</id><value>49.22</value></variable>'
                '<variable><id>papt</id><value>88.07</value></variable>'
                '<variable><id>pac1</id><value>0.00</value></variable>'
                '<variable><id>pac2</id><value>0.00</value></variable>'
                '<variable><id>pac3</id><value>0.00</value></variable>'
                '<variable><id>pact</id><value>0.00</value></variable>'
                '<variable><id>preac1</id><value>0.00</value></variable>'
                '<variable><id>preac2</id><value>0.00</value></variable>'
                '<variable><id>preac3</id><value>0.00</value></variable>'
                '<variable><id>preact</id><value>0.00</value></variable>'
                '<variable><id>freq1</id><value>50.00</value></variable>'
                '<variable><id>freq2</id><value>50.00</value></variable>'
                '<variable><id>freq3</id><value>50.00</value></variable>'
                '<variable><id>freqt</id><value>50.00</value></variable>'
                '<variable><id>fpot1</id><value>0.000</value></variable>'
                '<variable><id>fpot2</id><value>0.000</value></variable>'
                '<variable><id>fpot3</id><value>0.000</value></variable>'
                '<variable><id>fpott</id><value>0.000</value></variable>'
                '<variable><id>eac1</id><value>4</value></variable>'
                '<variable><id>eac2</id><value>22</value></variable>'
                '<variable><id>eac3</id><value>22</value></variable>'
                '<variable><id>eact</id><value>48</value></variable>'
                '<variable><id>ereactl1</id><value>0</value></variable>'
                '<variable><id>ereactl2</id><value>0</value></variable>'
                '<variable><id>ereactl3</id><value>0</value></variable>'
                '<variable><id>ereactlt</id><value>0</value></variable>'
                '<variable><id>ereactc1</id><value>0</value></variable>'
                '<variable><id>ereactc2</id><value>0</value></variable>'
                '<variable><id>ereactc3</id><value>0</value></variable>'
                '<variable><id>ereactct</id><value>0</value></variable>'
                '<variable><id>angle1</id><value>0.00</value></variable>'
                '<variable><id>angle2</id><value>0.00</value></variable>'
                '<variable><id>angle3</id><value>0.00</value></variable>'
                '<variable><id>scale</id><value>100</value></variable>'
                '</values>')
    else:
        valuesxml = '<values></values>'
    data = xmlheader + valuesxml
    print(f'{params}\n{data}')
    time.sleep(0.3)
    print(str(request.headers))
    headers = {
        "Cache-Control": 'no-cache',
        "Connection": 'close',
    }
    return Response(content=data, media_type="text/xml", headers=headers)


@app.get("/services/user/devices.xml")
async def services_devices(request: Request):
    print('devices.xml')
    global nombre
    data = ('<?xml version="1.0" encoding="UTF-8"?>\n\n'
        f'<devices>\n\t<id>{nombre}</id>\n</devices>')
    time.sleep(0.3)
    params = str(request.query_params)
    print(params)
    print(str(request.headers))
    headers = {
        "Cache-Control": 'no-cache',
        "Connection": 'close',
    }
    return Response(content=data, media_type="text/xml", headers=headers)


@app.get("/scan.cgi")
async def scanner(request: Request):
    print('scan.cgi')
    valorOK = '0'
    data = f'Success! {valorOK}'
    time.sleep(1)
    params = str(request.query_params)
    print(params)
    print(str(request.headers))
    headers = {
        "Cache-Control": 'no-cache',
        "Connection": 'close',
    }
    return Response(content=data, media_type="text/html", headers=headers)


@app.get("/scanresult.xml")
async def scanresult(request: Request):
    print('scanresult.xml')
    # data = """<?xml version="1.0" encoding="UTF-8"?>
    # <response><scan>0</scan><ver>12556</ver><count>0</count><ssid>
    # yourwifinetwork</ssid></response>
    # """
    yomismo = (
        '<response>\n'
 	    '\t<scan>0</scan>\n'
	    '\t<ver>12556</ver>\n'
	    '\t<count>15</count>\n'
	    '\t<ssid>yourwifinetwork</ssid>\n\n'
	    '\t<bss>\n'
	    '\t\t<valid>1</valid>\n'
	    '\t\t<name>0</name>\n'
	    '\t\t<privacy>0</privacy>\n'
	    '\t\t<wlan>0</wlan>\n'
	    '\t\t<strength>1</strength>\n'
	    '\t</bss>\n\n'
        ' </response>')
    data = ('<?xml version="1.0" encoding="UTF-8"?>\n\n'
            f' {yomismo}')
    print(data)
    print(str(request.headers))
    headers = {
        "Cache-Control": 'no-cache',
        "Connection": 'close',
    }
    return Response(content=data, media_type="text/xml", headers=headers)


@app.get("/scanallresults.xml")
async def scanallresults(request: Request):
    print('scanallresults.xml')
    red = '<response><scan>0</scan><ver>12556</ver><count>0</count><ssid>yourwifinetwork</ssid></response>'
    redes = """<response><scan>0</scan><ver>12556</ver><count>15</count><ssid>WIBEEE1234</ssid><bss><valid>1</valid><name>ORANGE&#x20;CASA</name><privacy>9</privacy><strength>2</strength></bss><bss><valid>1</valid><name>vodafoneBA1422</name><privacy>9</privacy><strength>2</strength></bss><bss><valid>1</valid><name>TP&#x2D;LINK&#x5F;34E9A4</name><privacy>13</privacy><strength>1</strength></bss><bss><valid>1</valid><name>Livebox6&#x2D;59DF</name><privacy>9</privacy><strength>1</strength></bss><bss><valid>1</valid><name>devolo&#x2D;105</name><privacy>9</privacy><strength>1</strength></bss><bss><valid>1</valid><name>MiFibra&#x2D;1234</name><privacy>9</privacy><strength>4</strength></bss><bss><valid>1</valid><name>MiFibra&#x2D;6789</name><privacy>9</privacy><strength>4</strength></bss><bss><valid>1</valid><name>Wifitv</name><privacy>9</privacy><strength>3</strength></bss><bss><valid>1</valid><name>Wifitv</name><privacy>9</privacy><strength>3</strength></bss><bss><valid>1</valid><name>WIFI</name><privacy>9</privacy><strength>3</strength></bss><bss><valid>1</valid><name>WLAN&#x5F;41</name><privacy>1</privacy><strength>2</strength></bss><bss><valid>1</valid><name>MOVISTAR&#x5F;710C</name><privacy>13</privacy><strength>3</strength></bss><bss><valid>1</valid><name>MOVISTAR&#x5F;3EFB</name><privacy>9</privacy><strength>1</strength></bss><bss><valid>1</valid><name>MOVISTAR&#x5F;F6E0</name><privacy>9</privacy><strength>1</strength></bss><bss><valid>1</valid><name>vodafone97B0</name><privacy>9</privacy><strength>1</strength></bss></response>"""
    data = ('<?xml version="1.0" encoding="UTF-8"?>\n\n'
            f' {redes}')
    print(str(request.headers))
    return Response(content=data, media_type="text/xml")


@app.get("/Wibeee/receiverAvg", tags=["basic"])
async def receiveData(args: Wibeee = Depends()):
    import datetime
    global primeravez
    x = args.dict()
    t = int(x['time'])
    # time.time()
    dt = datetime.datetime.fromtimestamp(t).isoformat()
    dt2 = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
    n = datetime.datetime.now()
    now = n.strftime('%Y-%m-%d %H:%M:%S')
    nowstr = n.strftime('%Y%m%dT%H')
    msg = f'time:{t} is {dt2} received at {now}\n{x}\n'
    print(msg)
    f = open(f"data_{nowstr}.txt", "a")
    f.write(msg)
    f.close()
    # Enviar respuesta
    if primeravez:
        primeravez = False
        txt_response = '<<<WREBOOT Thu Nov 04 10:53:24 UTC 2021'
    else:
        txt_response = '<<<WBAVG'
    time.sleep(0.2)
    print(txt_response)
    return txt_response


if __name__ == '__main__':
    uvicorn.run(
        'minimal_server:app',
        host='0.0.0.0',
        port=80,
        reload=True,
        debug=True,
        server_header=False
    )