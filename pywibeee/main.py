#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Command line interface (CLI) for WiBeee (old Mirubee) meter."""

from pywibeee import __version__

import argparse
import socket
from xml.etree import ElementTree
import sys
import time
import xmltodict
import json
import asyncio
import httpx
from multiprocessing import Process, Queue


class WiBeee():
    """WiBeee class."""

    def __init__(self, host=None, port=80, timeout=10.0, ucm='async'):
        """First init class."""
        self.host = host
        # Default host: 192.168.1.150
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
        self._useAsync = 'async' in ucm

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
            result = self.callurl(resource)
            if result and '<title>WiBeee</title>' in result:
                self.host = host
                found = True
                break
        return found

    async def autodiscoverAsync(self):
        """Autodiscover async WiBeee host."""
        found = False
        found_ips = self.checkSubnetOpenPort(self.getSubnet())
        for host in found_ips:
            resource = f'http://{host}:{self._port}/en/login.html'
            result = await self.callurlAsync(resource)
            if result and '<title>WiBeee</title>' in result:
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
            result = self.callurl(resource)
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
            result = await self.callurlAsync(resource)
            if result:
                self.data = result
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
            result = self.callurl(resource)
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
            result = await self.callurlAsync(resource)
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

    def get_or_create_eventloop(self):
        try:
            return asyncio.get_event_loop()
        except RuntimeError as ex:
            if "There is no current event loop in thread" in str(ex):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return asyncio.get_event_loop()

    def asyncCall(self, calling, printTxt=True):
        """Provide async call."""
        r = None
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
        elif calling == 'configureServer':
            # printTxt is (server_ip, server_port) tuple in this case
            if isinstance(printTxt, tuple):
                server_ip, server_port = printTxt
                r = loop.run_until_complete(
                    self.configureServerAsync(server_ip, server_port))
            else:
                r = None
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

    def callurl(self, url):
        """Call URL function using httpx (synchronous)."""
        result = None
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url)
            result = response.text
        except httpx.TimeoutException:
            result = 'Error: Timeout'
        except httpx.ConnectError:
            result = 'Error: ConnectionError'
        except httpx.HTTPError:
            result = 'Error: RequestException'
        except Exception as e:
            result = 'Error: ' + str(e)
        return result

    async def callurlAsync(self, url):
        """Call URL function using httpx (asynchronous)."""
        result = None
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
            result = response.text
        except httpx.TimeoutException:
            result = 'Error: Timeout'
        except httpx.ConnectError:
            result = 'Error: ConnectionError'
        except httpx.HTTPError:
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
                    r = self.asyncCall('getModel', False)
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
                    r = self.asyncCall('getModel', False)
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
        result = self.callurl(resource)
        if result and 'Error' not in result:
            resource = f'http://{self.host}:{self._port}/en/index.html'
            result = self.callurl(resource)
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
        result = await self.callurlAsync(resource)
        if result and 'Error' not in result:
            resource = f'http://{self.host}:{self._port}/en/index.html'
            result = await self.callurlAsync(resource)
            if result:
                data = str(result)
            searchmodeltxt = 'var model = "'
            start = data.find(searchmodeltxt)
            if start != -1:
                end = data.find('"', start+len(searchmodeltxt))
                model = data[start+len(searchmodeltxt):end]
        return model

    # Model code to description mapping
    MODEL_DESCRIPTIONS = {
        'WBM': 'Wibeee 1Ph',
        'WBT': 'Wibeee 3Ph',
        'WMX': 'Wibeee MAX',
        'WTD': 'Wibeee 3Ph RN',
        'WX2': 'Wibeee MAX 2S',
        'WX3': 'Wibeee MAX 3S',
        'WXX': 'Wibeee MAX MS',
        'WBB': 'Wibeee BOX',
        'WB3': 'Wibeee BOX S3P',
        'W3P': 'Wibeee 3Ph 3W',
        'WGD': 'Wibeee GND',
        'WBP': 'Wibeee SMART PLUG',
    }

    def getModelDescription(self):
        """Provide model description from model."""
        self.modelDescription = self.MODEL_DESCRIPTIONS.get(
            self.model, 'Unknown'
        )

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
                        r = self.asyncCall('getModel', False)
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
        result = None
        self.actionName = 'rebootWeb'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/config_value?reboot=1'
            result = self.callurl(resource)
            if result and len(result) == 0:
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
            result = await self.callurlAsync(resource)
            if result and len(result) == 0:
                result = 'done'
        return self.outputAction(result)

    def resetEnergy(self):
        """Provide reset energy from web."""
        result = None
        self.actionName = 'resetEnergy'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            resource = f'http://{self.host}:{self._port}/resetEnergy?resetEn=1'
            result = self.callurl(resource)
            if result and len(result) == 0:
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
            result = await self.callurlAsync(resource)
            if result and len(result) == 0:
                result = 'done'
        return self.outputAction(result)

    def configureServer(self, server_ip, server_port=8600):
        """Configure the WiBeee to push data to a server.

        The WiBeee firmware expects the port in hexadecimal format.
        Example: 8600 decimal = 2198 hex, 8080 = 1f90 hex.

        After configuring, sends a reset so the device applies changes.

        Args:
            server_ip: IP address of the push server.
            server_port: Port in decimal (default 8600).

        Returns:
            Result string indicating success or failure.
        """
        result = 'ERROR'
        self.actionName = 'configureServer'
        if self.host is None:
            foundhost = self.autodiscover()
        else:
            foundhost = True
        if foundhost:
            port_hex = format(int(server_port), '04x')
            resource = (
                f'http://{self.host}:{self._port}/configura_server'
                f'?ipServidor={server_ip}'
                f'&URLServidor={server_ip}'
                f'&portServidor={port_hex}'
            )
            result = self.callurl(resource)
            if result and 'Error' not in result:
                # Reset the device to apply changes
                resource = (
                    f'http://{self.host}:{self._port}'
                    '/config_value?reset=true'
                )
                self.callurl(resource)
                result = f'done (server={server_ip}:{server_port})'
        return self.outputAction(result)

    async def configureServerAsync(self, server_ip, server_port=8600):
        """Provide async configure server push."""
        result = None
        self.actionName = 'configureServer'
        if self.host is None:
            foundhost = await self.autodiscoverAsync()
        else:
            foundhost = True
        if foundhost:
            port_hex = format(int(server_port), '04x')
            resource = (
                f'http://{self.host}:{self._port}/configura_server'
                f'?ipServidor={server_ip}'
                f'&URLServidor={server_ip}'
                f'&portServidor={port_hex}'
            )
            result = await self.callurlAsync(resource)
            if result is not None and 'Error' not in str(result):
                # Reset the device to apply changes
                reset_resource = (
                    f'http://{self.host}:{self._port}'
                    '/config_value?reset=true'
                )
                await self.callurlAsync(reset_resource)
                result = f'done (server={server_ip}:{server_port})'
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

    # Sensor type definitions: xml_key -> [display_name, unit, mdi_icon]
    SENSOR_DEFINITIONS = {
        'vrms': ['Vrms', 'V', 'mdi:sine-wave'],
        'irms': ['Irms', 'A', 'mdi:flash-auto'],
        'p_aparent': ['Apparent Power', 'VA', 'mdi:flash-circle'],
        'p_activa': ['Active Power', 'W', 'mdi:flash'],
        'p_reactiva_ind': ['Inductive Reactive Power', 'var',
                           'mdi:flash-outline'],
        'p_reactiva_cap': ['Capacitive Reactive Power', 'var',
                           'mdi:flash-outline'],
        'frecuencia': ['Frequency', 'Hz', 'mdi:current-ac'],
        'factor_potencia': ['Power Factor', ' ', 'mdi:math-cos'],
        'energia_activa': ['Active Energy', 'Wh', 'mdi:pulse'],
        'energia_reactiva_ind': ['Inductive Reactive Energy', 'varh',
                                 'mdi:alpha-e-circle-outline'],
        'energia_reactiva_cap': ['Capacitive Reactive Energy', 'varh',
                                 'mdi:alpha-e-circle-outline'],
        'angle': ['Angle', '\u00b0', 'mdi:angle-acute'],
        'thd_total': ['THD Current', '%', 'mdi:chart-bubble'],
        'thd_fund': ['THD Current (fundamental)', 'A', 'mdi:vector-point'],
        'thd_ar3': ['THD Current Harmonic 3', 'A', 'mdi:numeric-3'],
        'thd_ar5': ['THD Current Harmonic 5', 'A', 'mdi:numeric-5'],
        'thd_ar7': ['THD Current Harmonic 7', 'A', 'mdi:numeric-7'],
        'thd_ar9': ['THD Current Harmonic 9', 'A', 'mdi:numeric-9'],
        'thd_tot_V': ['THD Voltage', '%', 'mdi:chart-bubble'],
        'thd_fun_V': ['THD Voltage (fundamental)', 'V', 'mdi:vector-point'],
        'thd_ar3_V': ['THD Voltage Harmonic 3', 'V', 'mdi:numeric-3'],
        'thd_ar5_V': ['THD Voltage Harmonic 5', 'V', 'mdi:numeric-5'],
        'thd_ar7_V': ['THD Voltage Harmonic 7', 'V', 'mdi:numeric-7'],
        'thd_ar9_V': ['THD Voltage Harmonic 9', 'V', 'mdi:numeric-9'],
    }

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
                if name not in sensorTypes and name in self.SENSOR_DEFINITIONS:
                    sensorTypes[name] = self.SENSOR_DEFINITIONS[name]
        if self.outformat == 'plain':
            result = sensorTypes
        elif self.outformat == 'json':
            result = json.dumps(sensorTypes)
        elif self.outformat == 'xml':
            result = sensorTypes
        elif self.outformat == 'file':
            filename = 'sensorTypes.txt'
            f = open(filename, 'w')
            f.write(json.dumps(sensorTypes))
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
    parser.add_argument('-o', '--output', action='store', type=str, nargs=1,
                        choices=['xml', 'json', 'plain', 'file'],
                        help='xml|json|plain|file',
                        default='json')
    my_group.add_argument('-a', '--action', action='store', type=str, nargs=1,
                          choices=['reboot', 'rebootweb', 'resetenergy',
                                   'configureserver'],
                          help='reboot|rebootweb|resetenergy|configureserver')
    my_group.add_argument('-g', '--get', action='store', type=str, nargs=1,
                          choices=['model', 'version', 'status',
                                   'info', 'sensors', 'devicename'],
                          help='model|version|status|info|sensors|devicename')
    parser.add_argument('--serverip', action='store', type=str, nargs=1,
                        help='Server IP for push config (use with '
                             '-a configureserver)',
                        default=None)
    parser.add_argument('--serverport', action='store', type=int, nargs=1,
                        help='Server port for push config (default 8600)',
                        default=[8600])
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
    c = WiBeee(host, port, timeout)
    frm = args.output
    if frm:
        if isinstance(frm, list):
            c.setOutputFormat(frm[0])
        else:
            c.setOutputFormat(frm)
    if args.auto:
        c.asyncCall('autodiscover')
    if args.get:
        if args.get[0] == 'model':
            result = c.asyncCall('getModel')
        elif args.get[0] == 'version':
            result = c.getVersion()
        elif args.get[0] == 'status':
            result = c.asyncCall('getStatus')
        elif args.get[0] == 'info':
            result = c.asyncCall('getInfo')
        elif args.get[0] == 'sensors':
            result = c.getSensors()
        elif args.get[0] == 'devicename':
            result = c.asyncCall('getDeviceName')
    if args.action:
        if args.action[0] == 'reboot':
            result = c.reboot()
        elif args.action[0] == 'rebootweb':
            result = c.asyncCall('rebootWeb')
        elif args.action[0] == 'resetenergy':
            result = c.asyncCall('resetEnergy')
        elif args.action[0] == 'configureserver':
            server_ip = args.serverip[0] if args.serverip else c.getIp()
            server_port = args.serverport[0] if args.serverport else 8600
            result = c.asyncCall(
                'configureServer', (server_ip, server_port))
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
