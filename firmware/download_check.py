#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR    | DATE       | VERSION | COMMENTS
# F.Quinto  | 2022-07-30 | 0.0.0   | First version

"""Firmware downloader.

sudo -H pip3 install httpx
"""

import httpx

download = True
continueWhiling = True
v1 = 3
v2 = 4
v3 = 600
# v1 = 4
# v2 = 4
# v3 = 123
models = [
    'WBB',
    'WB3'
]
print('Starting!')
while continueWhiling:
    for model in models:
        fname = f'FOTAFile_V{v1}.{v2}.{v3}_{model}.bin'
        model_lower = model.lower()
        url = f'https://app.mirubee.com/api/fw/{model_lower}/{fname}'
        # print(f'Trying {url}...')
        print(f'Checking version {v1}.{v2}.{v3} and model {model}...', end='', flush=True)
        if download:
            with httpx.Client() as client:
                r = client.get(url)
                if r.status_code == 200:
                    print(f'\n\n{url} Found!\n')
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
