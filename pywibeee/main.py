#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Command line interface (CLI) for WiBeee (old Mirubee) meter."""

__version__ = "0.0.6"

import argparse
import requests
import socket
from xml.etree import ElementTree
import sys
import time
import xmltodict
import json
import aiohttp
import asyncio
import httpx
from multiprocessing import Process, Queue


class WiBeee():
    """WiBeee class."""

    def __init__(self, host=None, port=80, timeout=10.0, ucm='async_httpx'):
        """First init class."""
        self.host = host
        # Default host: 192.168.1.150
        self._request = None
        self.session = None
        self._port = int(port)
        self._timeout = float(timeout)
        self.data = None
        self.cmdport = 550
        self.model = None
        self.modelDescription = None
        self.version = None
        self.deviceName = None
        self.outformat = 'json'
        self.timedata = None
        self.actionName = None
        if 'async' in ucm:
            self._useAsync = True
            self._asynctype = ucm
        else:
            self._useAsync = False
            self._asynctype = None

    def getIp(self):
        """Get own IP."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            s.connect(('<broadcast>', 0))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        return ip

    def getSubnet(self):
        """Get own subnet."""
        own_ip = self.getIp()
        ip_split = own_ip.split('.')
        subnet = ip_split[:-1]
        subnetstr = '.'.join(subnet)
        return subnetstr

    def check_server(self, address, queue, port):
        """Check an IP and port for it to be open, store result in queue."""
        # Create a TCP socket
        s = socket.socket()
        try:
            s.connect((address, port))
            queue.put((True, address, port))
        except socket.error:
            queue.put((False, address, port))

    def checkSubnetOpenPort(self, subnet):
        """Check subnet for open port IPs."""
        q = Queue()
        processes = []
        port1 = self._port
        for i in range(1, 255):
            ip = f'{subnet}.{i}'
            p = Process(target=self.check_server, args=[ip, q, port1])
            processes.append(p)
            p.start()
        found_ips = []
        for idx, p in enumerate(processes):
            if p.exitcode is None:
                p.terminate()
            else:
                # If finished, check if the port was open
                open_ip, address, port = q.get()
                if open_ip:
                    found_ips.append(address)
        #  Cleanup processes
        for idx, p in enumerate(processes):
            p.join()
        return found_ips

    def autodiscover(self):
        """Autodiscover WiBeee host."""
        found = False
        found_ips = self.checkSubnetOpenPort(self.getSubnet())
        for host in found_ips:
            resource = f'http://{host}:{self._port}/en/login.html'
            self._request = requests.Request("GET", resource).prepare()
            result = self.callurl()
            if '<title>WiBeee</title>' in result:
                self.host = host
                found = True
                break
        return found

    async def autodiscoverAsync(self):
        """Autodiscover async WiBeee host."""
        found = False
        found_ips = self.checkSubnetOpenPort(self.getSubnet())
        if self.session != None:
            self.session = None
            return found
        for host in found_ips:
            result = ''
            resource = f'http://{host}:{self._port}/en/login.html'
            if self._asynctype == 'async_aiohttp':
                self.session = aiohttp.ClientSession()
                async with self.session.get(resource) as resp:
                    #if resp.status == 200:
                    r = await resp.text(errors='ignore')
                    result = r
                await self.session.close()
            elif self._asynctype == 'async_httpx':
                self.session = httpx.AsyncClient()
                async with self.session as resp:
                    r = await resp.get(resource)
                    result = r.text
            if '<title>WiBeee</title>' in result:
                self.host = host
                found = True
                break
        return found

    def getStatus(self, printTxt=True):
        """Provide status."""
        self.data = 'ERROR'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/en/status.xml'
            self._request = requests.Request("GET", resource).prepare()
            result = self.callurl()
            if result:
                self.data = result
        if printTxt:
            return self.outputStatus()

    async def getStatusAsync(self, printTxt=True):
        """Provide async status."""
        self.data = 'ERROR'
        if self.host is None:
            foundhost = await self.autodiscoverAsync()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/en/status.xml'
            if self.session != None:
                self.session = None
            if self.session is None:
                if self._asynctype == 'async_aiohttp':
                    self.session = aiohttp.ClientSession()
                    async with self.session.get(resource) as resp:
                        assert resp.status == 200
                        r = await resp.text()
                        self.data = r
                    await self.session.close()
                elif self._asynctype == 'async_httpx':
                    self.session = httpx.AsyncClient()
                    async with self.session as resp:
                        r = await resp.get(resource)
                        self.data = r.text
                else:
                    result = 'ERROR'
                    return result
            if printTxt:
                return self.outputStatus()

    def getDeviceName(self, printTxt=True):
        """Provide device name."""
        result = 'ERROR'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/services/user/devices.xml'
            self._request = requests.Request("GET", resource).prepare()
            result = self.callurl()
            if result:
                self.data = result
                self.deviceName = self.getParameterXML('id')
                if not self.deviceName:
                    self.deviceName = 'ERROR'
        if printTxt:
            if self.outformat == 'json':
                result = self.outputJsonParam('devicename', self.deviceName)
            elif self.outformat == 'plain':
                result = self.deviceName
            elif self.outformat == 'xml':
                result = '<devicename>' + self.deviceName + '</devicename>'
            elif self.outformat == 'file':
                if not self.version:
                    self.getVersion(printTxt=False)
                filename = self.deviceName + '_' + self.version + '.xml'
                f = open(filename, 'w')
                f.write(self.deviceName)
                f.close()
                result = 'File saved!'
            return result

    async def getDeviceNameAsync(self, printTxt=True):
        """Provide async device name."""
        result = 'ERROR'
        if self.host is None:
            foundhost = await self.autodiscoverAsync()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/services/user/devices.xml'
            if self.session != None:
                self.session = None
            if self.session is None:
                if self._asynctype == 'async_aiohttp':
                    self.session = aiohttp.ClientSession()
                    async with self.session.get(resource) as resp:
                        assert resp.status == 200
                        r = await resp.text()
                        self.data = r
                        self.deviceName = self.getParameterXML('id')
                    await self.session.close()
                elif self._asynctype == 'async_httpx':
                    self.session = httpx.AsyncClient()
                    async with self.session as resp:
                        r = await resp.get(resource)
                        self.data = r.text
                        self.deviceName = self.getParameterXML('id')
                        if not self.deviceName:
                            self.deviceName = 'ERROR'
                else:
                    result = 'ERROR'
                    return result
            if printTxt:
                if self.outformat == 'json':
                    result = self.outputJsonParam('devicename', self.deviceName)
                elif self.outformat == 'plain':
                    result = self.deviceName
                elif self.outformat == 'xml':
                    result = '<devicename>' + self.deviceName + '</devicename>'
                elif self.outformat == 'file':
                    if not self.version:
                        self.getVersion(printTxt=False)
                    filename = self.deviceName + '_' + self.version + '.xml'
                    f = open(filename, 'w')
                    f.write(self.deviceName)
                    f.close()
                    result = 'File saved!'
                return result

    def get_or_create_eventloop(self):
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()

    def asyncCall(self, calling, asynctype='async_httpx', printTxt=True):
        """Provide async call."""
        r = None
        self._asynctype = asynctype
        loop = asyncio.get_event_loop()
        if calling == 'getStatus':
            r = loop.run_until_complete(self.getStatusAsync(printTxt))
        elif calling == 'autodiscover':
            r = loop.run_until_complete(self.autodiscoverAsync())
        elif calling == 'getInfo':
            r = loop.run_until_complete(self.getInfoAsync())
        elif calling == 'getModel':
            r = loop.run_until_complete(self.getModelAsync(printTxt))
        elif calling == 'getDeviceName':
            r = loop.run_until_complete(self.getDeviceNameAsync(printTxt))
        elif calling == 'rebootWeb':
            r = loop.run_until_complete(self.rebootWebAsync())
        elif calling == 'resetEnergy':
            r = loop.run_until_complete(self.resetEnergyAsync())
        return r

    def setPort(self, port):
        """Set port value."""
        self._port = int(port)

    def setTimeout(self, timeout):
        """Set timeout value."""
        self._timeout = float(timeout)

    def setOutputFormat(self, outformat):
        """Set output format."""
        self.outformat = outformat

    def callurl(self):
        """Call URL function."""
        result = None
        try:
            with requests.Session() as sess:
                response = sess.send(
                    self._request, timeout=self._timeout
                )
            result = response.text
        except requests.exceptions.Timeout:
            result = 'Error: Timeout'
        except requests.exceptions.ConnectionError:
            result = 'Error: ConnectionError'
        except requests.exceptions.RequestException:
            result = 'Error: RequestException'
        except Exception as e:
            result = 'Error: ' + str(e)
        return result

    def getInfo(self):
        """Get all info."""
        result = 'ERROR'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            if not self.model:
                self.getModel(printTxt=False)
                self.getModelDescription()
            if not self.version:
                self.getVersion(printTxt=False)
            if not self.deviceName:
                self.getDeviceName(printTxt=False)
        result = self.outputJsonParam('model', self.model)
        result = self.outputJsonParam('model_description',
                                      self.modelDescription, result)
        result = self.outputJsonParam('webversion', self.version, result)
        result = self.outputJsonParam('host', self.host, result)
        result = self.outputJsonParam('devicename', self.deviceName, result)
        return result

    async def getInfoAsync(self):
        """Get async all info."""
        result = 'ERROR'
        if self.host is None:
            foundhost = await self.autodiscoverAsync()
        else:
            foundhost = True
        if foundhost:
            if not self.model:
                await self.getModelAsync(printTxt=False)
                self.getModelDescription()
            if not self.version:
                self.getVersion(printTxt=False)
            if not self.deviceName:
                await self.getDeviceNameAsync(printTxt=False)
        result = self.outputJsonParam('model', self.model)
        result = self.outputJsonParam('model_description',
                                      self.modelDescription, result)
        result = self.outputJsonParam('webversion', self.version, result)
        result = self.outputJsonParam('host', self.host, result)
        result = self.outputJsonParam('devicename', self.deviceName, result)
        return result

    def outputJsonParam(self, parameter, value, oldData=None):
        """Provide output JSON parameter and value."""
        if not oldData:
            root = xmltodict.parse('<response></response>')
        else:
            root = json.loads(oldData)
        if root['response'] is None:
            root['response'] = {}
        root['response'][parameter] = value
        return json.dumps(root)

    def outputStatus(self, param=None, value=None):
        """Provide output."""
        result = 'ERROR'
        if not self.data:
            self.getStatus()
        if self.outformat == 'xml' or self.outformat == 'plain':
            result = self.data
        elif self.outformat == 'json':
            try:
                root = xmltodict.parse(self.data)
            except Exception:
                root = xmltodict.parse('<response></response>')
                root['response'] = {}
                root['response']['model'] = 'ERROR'
                root['response']['model_description'] = 'ERROR'
                root['response']['webversion'] = 'ERROR'
                self.timedata = self.getTimeData()
                root['response']['time'] = self.timedata
                result = json.dumps(root)
                return result
            if 'model' not in self.data:
                if self._useAsync:
                    r = self.asyncCall('getModel', self._asynctype, False)
                else:
                    self.getModel(printTxt=False)
                if not 'response' in root:
                    root['response'] = {}
                root['response']['model'] = self.model
            else:
                self.model = root['response']['model']
            if 'model_description' not in self.data:
                self.getModelDescription()
                if not 'response' in root:
                    root['response'] = {}
                root['response']['model_description'] = self.modelDescription
            if 'webversion' not in self.data:
                self.getVersion(printTxt=False)
                if not 'response' in root:
                    root['response'] = {}
                root['response']['webversion'] = self.version
            if 'time' not in self.data:
                self.timedata = self.getTimeData()
                if not 'response' in root:
                    root['response'] = {}
                root['response']['time'] = self.timedata
            result = json.dumps(root)
        elif self.outformat == 'file':
            if not self.model:
                if self._useAsync:
                    r = self.asyncCall('getModel', self._asynctype, False)
                else:
                    self.getModel(printTxt=False)
                self.getModelDescription()
            if not self.version:
                self.getVersion(printTxt=False)
            filename = 'status_' + self.model + '_' + self.version + '.xml'
            f = open(filename, 'w')
            f.write(self.data)
            f.close()
            result = 'File saved!'
        return result

    def outputAction(self, data):
        """Provide output for action."""
        result = 'ERROR'
        if data:
            result = data
        if self.outformat == 'plain':
            result = 'action ' + self.actionName + ' ' + result
        elif self.outformat == 'xml':
            result = ('<action id="' + self.actionName + '">' + result
                      + '</action>')
        elif self.outformat == 'json':
            result = self.outputJsonParam(self.actionName, result)
        elif self.outformat == 'file':
            filename = 'action_' + self.actionName + '.txt'
            f = open(filename, 'w')
            f.write(result)
            f.close()
            result = 'File saved!'
        return result

    def getModel(self, printTxt=True):
        """Provide model."""
        result = 'ERROR'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            self.model = self.getParameterXML('model')
            if not self.model:
                self.model = 'ERROR'
                if foundhost:
                    self.model = self.getModelWeb()
            if self.modelDescription is None:
                self.getModelDescription()
        if printTxt:
            if self.outformat == 'json':
                result = self.outputJsonParam('model', self.model)
                result = self.outputJsonParam('model_description',
                                      self.modelDescription, result)
            elif self.outformat == 'plain':
                result = self.model + ' ' + self.modelDescription
            elif self.outformat == 'xml':
                result = '<model>' + self.model + '</model>'
            elif self.outformat == 'file':
                if not self.version:
                    self.getVersion(printTxt=False)
                filename = self.model + '_' + self.version + '.xml'
                f = open(filename, 'w')
                f.write(self.model)
                f.close()
                result = 'File saved!'
            return result

    async def getModelAsync(self, printTxt=True):
        """Provide async model."""
        result = 'ERROR'
        if self.host is None:
            foundhost = await self.autodiscoverAsync()
        else:
            foundhost = True
        if foundhost:
            self.model = self.getParameterXML('model')
            if not self.model:
                self.model = 'ERROR'
                if foundhost:
                    self.model = await self.getModelWebAsync()
            if self.modelDescription is None:
                self.getModelDescription()
        if printTxt:
            if self.outformat == 'json':
                result = self.outputJsonParam('model', self.model)
                result = self.outputJsonParam('model_description',
                                      self.modelDescription, result)
            elif self.outformat == 'plain':
                result = self.model + ' ' + self.modelDescription
            elif self.outformat == 'xml':
                result = '<model>' + self.model + '</model>'
            elif self.outformat == 'file':
                if not self.version:
                    self.getVersion(printTxt=False)
                filename = self.model + '_' + self.version + '.xml'
                f = open(filename, 'w')
                f.write(self.model)
                f.close()
                result = 'File saved!'
            return result

    def getModelWeb(self):
        """Provide model from web."""
        model = 'ERROR'
        data = ''
        resource = (f'http://{self.host}:{self._port}/en/loginRedirect.html'
                    '?user=user&pwd=user')
        self._request = requests.Request("GET", resource).prepare()
        result = self.callurl()
        if result:
            resource = f'http://{self.host}:{self._port}/en/index.html'
            self._request = requests.Request("GET", resource).prepare()
            result = self.callurl()
            if result:
                data = str(result)
            searchmodeltxt = 'var model = "'
            start = data.find(searchmodeltxt)
            if start != -1:
                end = data.find('"', start+len(searchmodeltxt))
                model = data[start+len(searchmodeltxt):end]
        return model

    async def getModelWebAsync(self):
        """Provide async model from web."""
        model = 'ERROR'
        data = ''
        resource = (f'http://{self.host}:{self._port}/en/loginRedirect.html'
                    '?user=user&pwd=user')
        if self.session is None:
            if self._asynctype == 'async_aiohttp':
                self.session = aiohttp.ClientSession()
                async with self.session.get(resource) as resp:
                    assert resp.status == 200
                    r = await resp.text()
                    result = r
                await self.session.close()
            elif self._asynctype == 'async_httpx':
                self.session = httpx.AsyncClient()
                async with self.session as resp:
                    r = await resp.get(resource)
                    result = r.text
            else:
                return model

        # async with self.session.get as resp:
        #     r = await resp.get(resource)
        #     result = r.text

        if result:
            data = str(result)
        searchmodeltxt = 'var model = "'
        start = data.find(searchmodeltxt)
        if start != -1:
            end = data.find('"', start+len(searchmodeltxt))
            model = data[start+len(searchmodeltxt):end]
        return model

    def getModelDescription(self):
        """Provide model description from model."""
        self.modelDescription = 'Unknown'
        if self.model == 'WBM':
            self.modelDescription = 'Wibeee 1Ph'
        elif self.model == 'WBT':
            self.modelDescription = 'Wibeee 3Ph'
        elif self.model == 'WMX':
            self.modelDescription = 'Wibeee MAX'
        elif self.model == 'WTD':
            self.modelDescription = 'Wibeee 3Ph RN'
        elif self.model == 'WX2':
            self.modelDescription = 'Wibeee MAX 2S'
        elif self.model == 'WX3':
            self.modelDescription = 'Wibeee MAX 3S'
        elif self.model == 'WXX':
            self.modelDescription = 'Wibeee MAX MS'
        elif self.model == 'WBB':
            self.modelDescription = 'Wibeee BOX'
        elif self.model == 'WB3':
            self.modelDescription = 'Wibeee BOX S3P'
        elif self.model == 'W3P':
            self.modelDescription = 'Wibeee 3Ph 3W'
        elif self.model == 'WGD':
            self.modelDescription = 'Wibeee GND'
        elif self.model == 'WBP':
            self.modelDescription = 'Wibeee SMART PLUG'

    def getTimeData(self):
        """Provide now time."""
        import datetime
        now = datetime.datetime.now()
        return round(now.timestamp())

    def getVersion(self, printTxt=True):
        """Provide version from cmd."""
        result = 'ERROR'
        self.version = self.getParameterXML('webversion')
        if not self.version:
            resultCmd = self.doCmd(b'\x0d')
            if resultCmd:
                if not('Error:' in str(resultCmd)):
                    cleanversion = resultCmd[3:]
                    self.version = cleanversion.decode()
                else:
                    self.version = resultCmd
        if printTxt:
            if self.outformat == 'json':
                result = self.outputJsonParam('webversion', self.version)
            elif self.outformat == 'plain':
                result = self.version
            elif self.outformat == 'xml':
                result = '<webversion>' + self.version + '</webversion>'
            elif self.outformat == 'file':
                if not self.model:
                    if self._useAsync:
                        r = self.asyncCall('getModel', self._asynctype, False)
                    else:
                        self.getModel(printTxt=False)
                    self.getModelDescription()
                filename = self.model + '_' + self.version + '.xml'
                f = open(filename, 'w')
                f.write(self.version)
                f.close()
                result = 'File saved!'
            return result

    def readBackupPosition(self):
        """Provide backup position."""
        result = None
        self.actionName = 'readBackupPosition'
        resultCmd = self.doCmd(b'\x0f')
        if resultCmd:
            if not('Error:' in resultCmd):
                result = resultCmd.decode()
            else:
                result = resultCmd
        return self.outputAction(result)

    def reboot(self):
        """Provide reboot from command."""
        result = None
        self.actionName = 'reboot'
        resultCmd = self.doCmd(b'\x01')
        if resultCmd:
            if not('Error:' in resultCmd):
                result = resultCmd
        return self.outputAction(result)

    def rebootWeb(self):
        """Provide reboot from web."""
        result = 'ERROR'
        result = None
        self.actionName = 'rebootWeb'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/config_value?reboot=1'
            self._request = requests.Request("GET", resource).prepare()
            result = self.callurl()
            if len(result) == 0:
                result = 'done'
        return self.outputAction(result)

    async def rebootWebAsync(self):
        """Provide async reboot from web."""
        result = None
        self.actionName = 'rebootWeb'
        if self.host is None:
            foundhost = await self.autodiscoverAsync()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/config_value?reboot=1'
            if self.session is None:
                if self._asynctype == 'async_aiohttp':
                    self.session = aiohttp.ClientSession()
                    async with self.session.get(resource) as resp:
                        assert resp.status == 200
                        r = await resp.text()
                        result = r
                    await self.session.close()
                elif self._asynctype == 'async_httpx':
                    self.session = httpx.AsyncClient()
                    async with self.session as resp:
                        r = await resp.get(resource)
                        result = r.text
                else:
                    return result
            # async with self.session as resp:
            #     r = await resp.get(resource)
            #     result = r.text
            if len(result) == 0:
                result = 'done'
        return self.outputAction(result)

    def resetEnergy(self):
        """Provide reset energy from web."""
        result = 'ERROR'
        result = None
        self.actionName = 'resetEnergy'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/resetEnergy?resetEn=1'
            self._request = requests.Request("GET", resource).prepare()
            result = self.callurl()
            if result:
                if len(result) == 0:
                    result = 'done'
        return self.outputAction(result)

    async def resetEnergyAsync(self):
        """Provide async reset energy from web."""
        result = None
        self.actionName = 'resetEnergy'
        if self.host is None:
            foundhost = await self.autodiscoverAsync()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/resetEnergy?resetEn=1'
            if self._asynctype == 'async_aiohttp':
                self.session = aiohttp.ClientSession()
                async with self.session.get(resource) as resp:
                    assert resp.status == 200
                    r = await resp.text()
                    result = r
                await self.session.close()
            elif self._asynctype == 'async_httpx':
                self.session = httpx.AsyncClient()
                async with self.session as resp:
                    r = await resp.get(resource)
                    result = r.text
            else:
                return result
            # async with self.session as resp:
            #     r = await resp.get(resource)
            #     result = r.text
            if len(result) == 0:
                result = 'done'
        return self.outputAction(result)

    def doCmd(self, cmd):
        """Provide cmd interface to the meter."""
        result = None
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self._timeout)
        server_address = (self.host, self.cmdport)
        if self.host is not None and self.cmdport is not None:
            try:
                sock.connect(server_address)
            except socket.error as e:
                return 'Error: ' + str(e)
            try:
                sock.sendall(cmd)
                time.sleep(0.001)
                if cmd != b'\x01':
                    result = sock.recv(16)
            finally:
                sock.close()
        return result

    def getSensors(self):
        """Provide sensors list from XML."""
        result = 'ERROR'
        sensorTypes = {}
        if not self.data:
            self.getStatus(False)
        datavalue = str(self.data)
        try:
            xml = ElementTree.fromstring(datavalue)
        except Exception:
            xml = []
            return result
        for item in xml:
            if item.tag[:4] == 'fase':
                name = item.tag[6:]
                if name not in sensorTypes:
                    if name == 'vrms':
                        sensorTypes[name] = ['Vrms', 'V', 'mdi:power-plug']
                    elif name == 'irms':
                        sensorTypes[name] = ['Irms', 'A', 'mdi:flash-auto']
                    elif name == 'p_aparent':
                        sensorTypes[name] = ['Apparent Power', 'VA',
                                             'mdi:flash-circle']
                    elif name == 'p_activa':
                        sensorTypes[name] = ['Active Power', 'W', 'mdi:flash']
                    elif name == 'p_reactiva_ind':
                        sensorTypes[name] = ['Inductive Reactive Power',
                                             'VArL', 'mdi:flash-outline']
                    elif name == 'p_reactiva_cap':
                        sensorTypes[name] = ['Capacitive Reactive Power',
                                             'VArC', 'mdi:flash-outline']
                    elif name == 'frecuencia':
                        sensorTypes[name] = ['Frequency', 'Hz',
                                             'mdi:current-ac']
                    elif name == 'factor_potencia':
                        sensorTypes[name] = ['Power Factor', ' ',
                                             'mdi:math-cos']
                    elif name == 'energia_activa':
                        sensorTypes[name] = ['Active Energy',
                                             'Wh', 'mdi:pulse']
                    elif name == 'energia_reactiva_ind':
                        sensorTypes[name] = ['Inductive Reactive Energy',
                                             'VArLh',
                                             'mdi:alpha-e-circle-outline']
                    elif name == 'energia_reactiva_cap':
                        sensorTypes[name] = ['Capacitive Reactive Energy',
                                             'VArCh',
                                             'mdi:alpha-e-circle-outline']
                    elif name == 'angle':
                        sensorTypes[name] = ['Angle',
                                             '°',
                                             'mdi:angle-acute']
                    elif name == 'thd_total':
                        # Total Harmonic Distortion = THD
                        sensorTypes[name] = ['THD Current',
                                             '%',
                                             'mdi:chart-bubble']
                    elif name == 'thd_fund':
                        sensorTypes[name] = ['THD Current (fundamental)',
                                             'A',
                                             'mdi:vector-point']
                    elif name == 'thd_ar3':
                        sensorTypes[name] = ['THD Current Harmonic 3',
                                             'A',
                                             'mdi:numeric-3']
                    elif name == 'thd_ar5':
                        sensorTypes[name] = ['THD Current Harmonic 5',
                                             'A',
                                             'mdi:numeric-5']
                    elif name == 'thd_ar7':
                        sensorTypes[name] = ['THD Current Harmonic 7',
                                             'A',
                                             'mdi:numeric-7']
                    elif name == 'thd_ar9':
                        sensorTypes[name] = ['THD Current Harmonic 9',
                                             'A',
                                             'mdi:numeric-9']
                    elif name == 'thd_tot_V':
                        sensorTypes[name] = ['THD Voltage',
                                             '%',
                                             'mdi:chart-bubble']
                    elif name == 'thd_fun_V':
                        sensorTypes[name] = ['THD Voltage (fundamental)',
                                             'V',
                                             'mdi:vector-point']
                    elif name == 'thd_ar3_V':
                        sensorTypes[name] = ['THD Voltage Harmonic 3',
                                             'V',
                                             'mdi:numeric-3']
                    elif name == 'thd_ar5_V':
                        sensorTypes[name] = ['THD Voltage Harmonic 5',
                                             'V',
                                             'mdi:numeric-5']
                    elif name == 'thd_ar7_V':
                        sensorTypes[name] = ['THD Voltage Harmonic 7',
                                             'V',
                                             'mdi:numeric-7']
                    elif name == 'thd_ar9_V':
                        sensorTypes[name] = ['THD Voltage Harmonic 9',
                                             'V',
                                             'mdi:numeric-9']
        if self.outformat == 'plain':
            result = sensorTypes
        elif self.outformat == 'json':
            result = json.dumps(sensorTypes)
        elif self.outformat == 'xml':
            result = sensorTypes
        elif self.outformat == 'file':
            filename = 'sensorTypes.txt'
            f = open(filename, 'w')
            f.write(sensorTypes)
            f.close()
            result = 'File saved!'
        return result

    def getParameterXML(self, param):
        """Provide parameter value from XML."""
        parametervalue = None
        if not self.data:
            self.getStatus(False)
        datavalue = str(self.data)
        if param in datavalue:
            xml = ElementTree.fromstring(datavalue)
            for item in xml:
                if item.tag == param:
                    parametervalue = item.text
                    break
        return parametervalue


def parsing_args(arguments):
    """Parse arguments."""
    des = 'CLI for WiBeee (old Mirubee) meter'
    frm = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(prog='pywibeee',
                                     # usage='%(prog)s [options] path',
                                     description=des,
                                     formatter_class=frm,
                                     epilog='Enjoy! :)')
    host_group = parser.add_mutually_exclusive_group(required=True)
    my_group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-version', '--version',
                        action='version',
                        version='%(prog)s '+__version__)
    host_group.add_argument('--host',
                            action='store',
                            type=str,
                            nargs=1,
                            help='The host (or the IP) of the meter.')
    host_group.add_argument('--auto',
                            action='store_true',
                            help='Autodiscover host function, look IP on net.')
    parser.add_argument('-p', '--port', action='store', type=str,
                        nargs=1,
                        help='set port (default 80)',
                        default='80')
    parser.add_argument('-t', '--settimeout', action='store', type=str,
                        nargs=1,
                        help='set timeout in seconds (default 10.0)',
                        default='10.0')
    parser.add_argument('-m', '--urlcallmethod', action='store', type=str,
                        nargs=1,
                        choices=['async_httpx', 'async_aiohttp', 'request'],
                        help='set URL call method (default async_httpx)',
                        default='async_httpx')
    parser.add_argument('-o', '--output', action='store', type=str, nargs=1,
                        choices=['xml', 'json', 'plain', 'file'],
                        help='xml|json|plain|file',
                        default='json')
    my_group.add_argument('-a', '--action', action='store', type=str, nargs=1,
                          choices=['reboot', 'rebootweb', 'resetenergy'],
                          help='reboot|rebootweb|resetenergy')
    my_group.add_argument('-g', '--get', action='store', type=str, nargs=1,
                          choices=['model', 'version', 'status',
                                   'info', 'sensors', 'devicename'],
                          help='model|version|status|info|sensors|devicename')
    args = parser.parse_args(arguments)
    return args


def program(args, printdata=True):
    """Mainly program."""
    result = None
    if args.host:
        host = (args.host)[0]
    else:
        host = None
    if args.port:
        port = args.port
    else:
        port = 80
    if args.settimeout:
        timeout = args.settimeout
    else:
        timeout = 10.0
    if args.urlcallmethod == 'async_httpx':
        ucm = 'async_httpx'
    else:
        ucm = (args.urlcallmethod)[0]
    c = WiBeee(host, port, timeout, ucm)
    frm = args.output
    if frm:
        if isinstance(frm, list):
            c.setOutputFormat(frm[0])
        else:
            c.setOutputFormat(frm)
    if args.auto:
        if ucm == 'async_httpx':
            c.asyncCall('autodiscover', ucm)
        elif ucm == 'async_aiohttp':
            c.asyncCall('autodiscover', ucm)
        else:
            c.autodiscover()
    if args.get:
        if args.get[0] == 'model':
            if 'async' in ucm:
                result = c.asyncCall('getModel', ucm)
            else:
                result = c.getModel()
        elif args.get[0] == 'version':
            result = c.getVersion()
        elif args.get[0] == 'status':
            if 'async' in ucm:
                result = c.asyncCall('getStatus', ucm)
            else:
                result = c.getStatus()
        elif args.get[0] == 'info':
            if 'async' in ucm:
                result = c.asyncCall('getInfo', ucm)
            else:
                result = c.getInfo()
        elif args.get[0] == 'sensors':
            result = c.getSensors()
        elif args.get[0] == 'devicename':
            if 'async' in ucm:
                result = c.asyncCall('getDeviceName', ucm)
            else:
                result = c.getDeviceName()
    if args.action:
        if args.action[0] == 'reboot':
            result = c.reboot()
        elif args.action[0] == 'rebootweb':
            if 'async' in ucm:
                result = c.asyncCall('rebootWeb', ucm)
            else:
                result = c.rebootWeb()
        elif args.action[0] == 'resetenergy':
            if 'async' in ucm:
                result = c.asyncCall('resetEnergy', ucm)
            else:
                result = c.resetEnergy()
    if printdata:
        print(result)
    else:
        return result


def main():
    """Mainly function."""
    args = parsing_args(sys.argv[1:])
    program(args)


if __name__ == "__main__":
    main()
