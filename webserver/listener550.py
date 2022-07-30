#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR    | DATE       | VERSION | COMMENTS
# F.Quinto  | 2021-07-20 | 0.0.0   | First draft

__version__ = "0.0.0"
"""Listener TCP 550 port."""


import socket
import sys
import time

enviarREALwibeee = True

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = ('0.0.0.0', 550)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
f = open('datos_firmware_recibido.bin','wb')
# Listen for incoming connections
sock.listen(1)
recibo0 = b'\r\x00\x00'
envio0 = b'\x8d\x00\x073.4.614'
recibo1 = b'\x0f\x00\x00'
envio1 = b'\x8f\x00\x00%\x00 \x00\x00'
recibo2 = b'\x08\x00\x04\x000\x00\x00'
envio2 = b'\x88\x00\x01%'
recibo3 = 'xxxxxx'
envio3 = b'\x86\x00\x01%'
# Cuando está todo enviado = 0b 00 08 00 30 00 00 00 04 8c b0 
recibo4 = b'\x0b\x00\x08\x000\x00\x00\x00\x04\x8c\xb0'
envio4 = b'\x8b\x00\x03\x25\x5e\xf2'

# es una cabecera de datos?
nosequees = b'\x06\x00\xfd\x00\x30'
# Connect WIBEEE
if enviarREALwibeee:
    s = socket.socket()
    host = '192.168.0.1'
    port = 550
    s.connect((host, port))
if enviarREALwibeee:
    tcritic = 0.0065
else:
    tcritic = 0.00001
while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = None
            recibo = None
            try:
                data = connection.recv(1024)
            except Exception as e:
                print('Exception: {}'.format(e))
                pass
            if data:
                print('De App a WIBEEE: {!r}'.format(data))
                # Guardo en archivo
                f.write(data)
                if enviarREALwibeee:
                    try:
                        # Envio data a WIBEE real
                        s.send(data)
                        time.sleep(tcritic)
                        recibirDeWibeee = True
                    except Exception as e:
                        print(f'Exception, parece que WIBEEE no responde: {e}')
                        time.sleep(0.025)
                        pass
                else:
                    # Envio data a WIBEE simulado
                    if data == recibo0:
                        connection.send(envio0)
                        print(f'Contesto 0: {envio0}')
                    elif data == recibo1:
                        connection.send(envio1)
                        print(f'Contesto 1: {envio1}')
                    elif data == recibo2:
                        connection.send(envio2)
                        print(f'Contesto 2: {envio2}')
                    elif data == recibo4:
                        connection.send(envio4)
                        print(f'Contesto 4: {envio4}')
                    else:
                        connection.send(envio3)
                        print(f'Contesto 3: {envio3}')
                    time.sleep(tcritic)
            else:
                print('no data from App')
                time.sleep(0.2)
            if enviarREALwibeee:
                while recibirDeWibeee:
                    try:
                        recibo = s.recv(1024)
                    except Exception as e:
                        print('Exception: {}'.format(e))
                        pass
                    if recibo:
                        print('De WIBEEE a App: {!r}'.format(recibo))
                        # Envio recibo a la App
                        connection.send(recibo)
                        time.sleep(tcritic)
                        recibirDeWibeee = False
                    else:
                        print('no data from WIBEE')
                        time.sleep(0.4)
                        # try:
                        #     print('simulo que WIBEE responde a App')
                        #     connection.send(b'\x86\x00\x01%')
                        # except Exception as e:
                        #     print('Ya no recibe APP')
                        #     break
            time.sleep(0.0001)

    finally:
        # Clean up the connection
        connection.close()
        f.close()