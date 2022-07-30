#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR    | DATE       | VERSION | COMMENTS
# F.Quinto  | 2021-11-05 | 0.0.0   | First draft

__version__ = "0.0.0"
"""Sender TCP 550 port."""


import socket               # Import socket module
import time

tw = 0.2

s = socket.socket()         # Create a socket object
# host = socket.gethostname() # Get local machine name
host = '192.168.0.1'
port = 550                  # Reserve a port for your service.

s.connect((host, port))
# s.send("Hello server!")
f = open('FOTAFile_V3.4.614_WBB.bin','rb')
print('Sending...')
l = f.read(1024)

data = b'\r\x00\x00'
s.send(data)
print(f'Sending 0 {data}...')
recibo = s.recv(1024)
print(f'Receiving 0 {recibo}...')
time.sleep(tw)

data = b'\x0f\x00\x00'
s.send(data)
print(f'Sending 1 {data}...')
recibo = s.recv(1024)
print(f'Receiving 1 {recibo}...')
time.sleep(tw)

data = b'\x08\x00\x04\x000\x00\x00'
s.send(data)
print(f'Sending 2 {data}...')
recibo = s.recv(1024)
print(f'Receiving 2 {recibo}...')
time.sleep(tw)

while (l):
    data = l
    s.send(data)
    print(f'Sending 3 {data}...')
    recibo = s.recv(1024)
    print(f'Receiving 3 {recibo}...')
    if b'\xaa' in recibo:
        print('Received malo?')
        time.sleep(tw)
    time.sleep(tw)
    l = f.read(1024)
f.close()

data = b'\x0b\x00\x08\x000\x00\x00\x00\x04\x8c\xb0'
s.send(data)
print(f'Sending 4 {data}...')
recibo = s.recv(1024)
print(f'Receiving 4 {recibo}...')

time.sleep(2)

s.close
