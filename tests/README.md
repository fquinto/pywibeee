# Quick testing

./main.py --host 192.168.1.150 --get model -m request
./main.py --host 192.168.1.150 --get version -m request
./main.py --host 192.168.1.150 --get status -m request
./main.py --host 192.168.1.150 --get info -m request
./main.py --host 192.168.1.150 --get sensors -m request
./main.py --host 192.168.1.150 --get devicename -m request
./main.py --auto --get model -m request
./main.py --auto --get version -m request
./main.py --auto --get status -m request
./main.py --auto --get info -m request
./main.py --auto --get sensors -m request
./main.py --auto --get devicename -m request

./main.py --host 192.168.1.150 --get model -m async_aiohttp
./main.py --host 192.168.1.150 --get version -m async_aiohttp
./main.py --host 192.168.1.150 --get status -m async_aiohttp
./main.py --host 192.168.1.150 --get info -m async_aiohttp
./main.py --host 192.168.1.150 --get sensors -m async_aiohttp
./main.py --host 192.168.1.150 --get devicename -m async_aiohttp
./main.py --auto --get model -m async_aiohttp
./main.py --auto --get version -m async_aiohttp
./main.py --auto --get status -m async_aiohttp
./main.py --auto --get info -m async_aiohttp
./main.py --auto --get sensors -m async_aiohttp
./main.py --auto --get devicename -m async_aiohttp

./main.py --host 192.168.1.150 --get model -m async_httpx
./main.py --host 192.168.1.150 --get version -m async_httpx
./main.py --host 192.168.1.150 --get status -m async_httpx
./main.py --host 192.168.1.150 --get info -m async_httpx
./main.py --host 192.168.1.150 --get sensors -m async_httpx
./main.py --host 192.168.1.150 --get devicename -m async_httpx
./main.py --auto --get model -m async_httpx
./main.py --auto --get version -m async_httpx
./main.py --auto --get status -m async_httpx
./main.py --auto --get info -m async_httpx
./main.py --auto --get sensors -m async_httpx
./main.py --auto --get devicename -m async_httpx

