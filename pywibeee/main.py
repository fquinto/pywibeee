#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Command line interface (CLI) for WiBeee (old Mirubee) meter."""

__version__ = "0.0.1"

import argparse
import requests
import socket
from xml.etree import ElementTree
import sys
import time
import jxmlease
import json
from multiprocessing import Process, Queue


class WiBeee():
    """WiBeee class."""

    def __init__(self, host='192.168.1.150', timeout=10):
        """First init class."""
        self.host = host
        self._request = None
        self._timeout = timeout
        self.data = None
        self.cmdport = 550
        self.model = None
        self.version = None
        self.outformat = 'json'
        self.timedata = None
        self.actionName = None

    def getIp(self):
        """Get own IP."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect(('<broadcast>', 0))
        return s.getsockname()[0]

    def getSubnet(self):
        """Get own subnet."""
        own_ip = self.getIp()
        ip_split = own_ip.split('.')
        subnet = ip_split[:-1]
        subnetstr = '.'.join(subnet)
        return subnetstr

    def check_server(self, address, queue, port=80):
        """Check an IP and port for it to be open, store result in queue."""
        # Create a TCP socket
        s = socket.socket()
        try:
            s.connect((address, port))
            # print("Connection open to %s on port %s" % (address, port))
            queue.put((True, address, port))
        except socket.error:
            queue.put((False, address, port))

    def checkSubnetOpenPort(self, subnet, port=80):
        """Check subnet for open port IPs."""
        q = Queue()
        processes = []
        for i in range(1, 255):
            ip = subnet + '.' + str(i)
            p = Process(target=self.check_server, args=[ip, q, port])
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
        found_ips = self.checkSubnetOpenPort(self.getSubnet())
        for host in found_ips:
            _RESOURCE = 'http://{}/en/login.html'
            resource = _RESOURCE.format(host)
            self._request = requests.Request("GET", resource).prepare()
            result = self.callurl()
            if '<title>WiBeee</title>' in result:
                self.host = host
                break
        return self.host

    def getStatus(self, printTxt=True):
        """Provide status."""
        _RESOURCE = 'http://{}/en/status.xml'
        resource = _RESOURCE.format(self.host)
        self._request = requests.Request("GET", resource).prepare()
        result = self.callurl()
        if result:
            self.data = result
        else:
            self.data = 'ERROR'
        if printTxt:
            return self.outputStatus()

    def setTimeout(self, timeout):
        """Set timeout value."""
        self._timeout = timeout

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
        except requests.exceptions.ConnectionError:
            result = 'Error: ConnectionError'
        except requests.exceptions.RequestException:
            result = 'Error: RequestException'
        except Exception as e:
            result = 'Error: ' + str(e)
        return result

    def getInfo(self):
        """Get all info."""
        if not self.model:
            self.getModel(printTxt=False)
        if not self.version:
            self.getVersion(printTxt=False)
        if self.host == '192.168.1.150':
            self.autodiscover()
        result = self.outputJsonParam('model', self.model)
        result = self.outputJsonParam('webversion', self.version, result)
        result = self.outputJsonParam('host', self.host, result)
        return result

    def outputJsonParam(self, parameter, value, oldData=None):
        """Provide output JSON parameter and value."""
        if not oldData:
            root = jxmlease.parse('<response></response>')
        else:
            root = oldData
        node = jxmlease.XMLCDATANode(value)
        root['response'].add_node(tag=parameter, new_node=node)
        return root

    def outputStatus(self):
        """Provide output."""
        result = 'ERROR'
        if not self.data:
            self.getStatus()
        if self.outformat == 'xml' or self.outformat == 'plain':
            result = self.data
        elif self.outformat == 'json':
            try:
                root = jxmlease.parse(self.data)
            except Exception:
                return result
            if 'model' not in self.data:
                self.getModel(printTxt=False)
                node = jxmlease.XMLCDATANode(self.model)
                root['response'].add_node(tag="model", new_node=node)
            if 'webversion' not in self.data:
                self.getVersion(printTxt=False)
                node = jxmlease.XMLCDATANode(self.version)
                root['response'].add_node(tag="webversion", new_node=node)
            if 'time' not in self.data:
                self.timedata = self.getTimeData()
                node = jxmlease.XMLCDATANode(self.timedata)
                root['response'].add_node(tag="time", new_node=node)
            result = root
        elif self.outformat == 'file':
            if not self.model:
                self.getModel(printTxt=False)
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
        self.model = self.getParameterXML('model')
        if not self.model:
            self.model = self.getModelWeb()
        if printTxt:
            if self.outformat == 'json':
                result = self.outputJsonParam('model', self.model)
            elif self.outformat == 'plain':
                result = self.model
            elif self.outformat == 'xml':
                result = '<model>' + self.version + '</model>'
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
        _RESOURCE = 'http://{}/en/loginRedirect.html?user=user&pwd=user'
        resource = _RESOURCE.format(self.host)
        self._request = requests.Request("GET", resource).prepare()
        result = self.callurl()
        if result:
            _RESOURCE = 'http://{}/en/index.html'
            resource = _RESOURCE.format(self.host)
            self._request = requests.Request("GET", resource).prepare()
            result = self.callurl()
            if result:
                data = str(result)
            searchmodeltxt = 'var model = "'
            start = data.find(searchmodeltxt)
            if start is not -1:
                end = data.find('"', start+len(searchmodeltxt))
                model = data[start+len(searchmodeltxt):end]
        return model

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
                if not('Error:' in resultCmd):
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
                    self.getModel(printTxt=False)
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
        _RESOURCE = 'http://{}/config_value?reboot=1'
        resource = _RESOURCE.format(self.host)
        self._request = requests.Request("GET", resource).prepare()
        result = self.callurl()
        if len(result) == 0:
            result = 'done'
        else:
            result = 'ERROR'
        return self.outputAction(result)

    def resetEnergy(self):
        """Provide reset energy from web."""
        result = None
        self.actionName = 'resetEnergy'
        _RESOURCE = 'http://{}/resetEnergy?resetEn=1'
        resource = _RESOURCE.format(self.host)
        self._request = requests.Request("GET", resource).prepare()
        result = self.callurl()
        if result:
            if len(result) == 0:
                result = 'done'
            else:
                result = 'ERROR'
        return self.outputAction(result)

    def doCmd(self, cmd):
        """Provide cmd interface to the meter."""
        result = None
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self._timeout)
        server_address = (self.host, self.cmdport)
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
            result = json.dumps(sensorTypes, indent=4)
        elif self.outformat == 'xml':
            result = jxmlease.emit_xml(sensorTypes)
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
    parser.add_argument('-t', '--settimeout', action='store', type=int,
                        nargs=1,
                        help='set timeout in seconds (default 10)')
    parser.add_argument('-o', '--output', action='store', type=str, nargs=1,
                        choices=['xml', 'json', 'plain', 'file'],
                        help='xml|json|plain|file',
                        default='json')
    my_group.add_argument('-a', '--action', action='store', type=str, nargs=1,
                          choices=['reboot', 'rebootweb', 'resetenergy'],
                          help='reboot|rebootweb|resetenergy')
    my_group.add_argument('-g', '--get', action='store', type=str, nargs=1,
                          choices=['model', 'version', 'status',
                                   'info', 'sensors'],
                          help='model|version|status|info|sensors')
    args = parser.parse_args(arguments)
    return args


def program(args, printdata=True):
    """Mainly program."""
    result = None
    if args.host:
        host = (args.host)[0]
    else:
        host = '192.168.1.150'
    if args.settimeout:
        timeout = args.settimeout[0]
    else:
        timeout = 10
    c = WiBeee(host, timeout)
    frm = args.output
    if frm:
        if isinstance(frm, list):
            c.setOutputFormat(frm[0])
        else:
            c.setOutputFormat(frm)
    if args.auto:
        c.autodiscover()
    if args.get:
        if args.get[0] == 'model':
            result = c.getModel()
        elif args.get[0] == 'version':
            result = c.getVersion()
        elif args.get[0] == 'status':
            result = c.getStatus()
        elif args.get[0] == 'info':
            result = c.getInfo()
        elif args.get[0] == 'sensors':
            result = c.getSensors()
    if args.action:
        if args.action[0] == 'reboot':
            result = c.reboot()
        elif args.action[0] == 'rebootweb':
            result = c.rebootWeb()
        elif args.action[0] == 'resetenergy':
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
