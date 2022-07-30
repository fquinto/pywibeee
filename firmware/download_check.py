#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib.request

download = True
continueWhiling = True
v1 = 3
v2 = 6
v3 = 0

while continueWhiling:
    
    fname = f'FOTAFile_V{v1}.{v2}.{v3}_WBB.bin'
    url = f'https://app.mirubee.com/api/fw/wbb/{fname}'
    print(f'Trying {url}...')
    if download:
        r = requests.get(url)
        if r.status_code == 200:
            print('Found!', end='')
            # print(r.status_code)
            # print(r.headers['content-type'])
            # print(r.encoding)
            with open(f'{fname}', 'wb') as f:
                f.write(r.content)
    v3 += 1
    if v3 > 999:
        v2 += 1
        v3 = 0
    if v2 > 99:
        v1 += 1
        v2 = 0
    if v1 > 5:
        continueWhiling = False

# urllib.request.urlretrieve(url, fname)
# r = requests.get(url, stream=True)
# print(r.headers)
