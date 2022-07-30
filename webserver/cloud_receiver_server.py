#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR    | DATE       | VERSION | COMMENTS
# F.Quinto  | 2021-07-20 | 0.0.0   | First draft
# F.Quinto  | 2021-11-10 | 0.0.1   | Clean receiver server

__version__ = "0.0.1"
"""Cloud receiver simulator server."""

from fastapi import FastAPI, Query, Depends, Request, Response
from pydantic import BaseModel
import uvicorn


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

app = FastAPI()

@app.get("/Wibeee/receiverAvg", tags=["basic"])
async def receiveData(args: Wibeee = Depends()):
    import datetime
    t = None
    dt2 = None
    x = args.dict()
    if 'time' in x:
        t = int(x['time'])
        dt = datetime.datetime.fromtimestamp(t).isoformat()
        dt2 = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
    n = datetime.datetime.now()
    now = n.strftime('%Y-%m-%d %H:%M:%S')
    nowstr = n.strftime('%Y%m%dT%H')
    # Show time and message data
    msg = f'time:"{t}" = "{dt2}" received at "{now}"\nDATA:{x}\n'
    print(msg)
    # Save data inside file
    f = open(f"data_{nowstr}.txt", "a")
    f.write(msg)
    f.close()
    # Enviar respuesta
    # txt_response = '<<<WREBOOT Thu Nov 04 10:53:24 UTC 2021'
    txt_response = '<<<WBAVG'
    # Return response
    return txt_response


if __name__ == '__main__':
    uvicorn.run(
        'cloud_receiver_server:app',
        host='0.0.0.0',
        port=8600,
        reload=True,
        debug=True,
        server_header=False
    )