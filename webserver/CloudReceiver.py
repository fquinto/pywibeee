#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR    | DATE       | VERSION | COMMENTS
# F.Quinto  | 2021-11-10 | 0.0.0   | First version


"""CloudReceiver.

Library to be installed:

sudo -H pip3 install redis
"""
import logging
import asyncio
import threading
logger = logging.getLogger("wibeee")
__version__ = "0.0.0"


class ListeningTCPSocket(asyncio.Protocol):
    """Listen TCP connection from ethernet."""

    def __init__(self, thread, useRedis):
        """Init of the class."""
        # Redis connection
        self.useRedis = useRedis
        self.clientRedis = None
        self.hostredis = 'localhost'
        self.portredis = 6379

        self.devices = {}
        self.routers = []
        self.valid_message = False
        self.transport = None
        self.ip = None
        self.peername = None
        # thread
        self.thread = thread

    def connection_made(self, transport: asyncio.Transport):
        """Call when a connection is made.

        The argument is the transport representing the pipe connection.
        To receive data, wait for data_received() calls.
        When the connection is closed, connection_lost() is called.
        """
        self.peername = transport.get_extra_info('peername')
        logger.info('Connection from {}'.format(self.peername))

        self.ip = self.peername[0]

        self.transport = transport
        if self.useRedis:
            self.redis_connection()

    def redis_connection(self, host=None, port=None, db=None):
        """Redis Connection."""
        # Connect to REDIS server
        if host:
            self.hostredis = host
        if port:
            self.portredis = port
        if not db:
            db = 0
        try:
            import redis
            self.clientRedis = redis.StrictRedis(host=self.hostredis,
                                                 port=self.portredis,
                                                 db=db)
            self.thread.setclientRedis(self.clientRedis)
        except Exception as e:
            logger.critical('Can NOT connect to Redis ' + str(e))

    def data_received(self, data: bytes):
        """Call when some data is received.

        The argument is a bytes object.
        """
        import urllib.parse
        mac = None
        ip = None
        version = None
        model = None
        # print(data)
        message_string = data.decode()
        params = message_string.split('?')
        if len(params) > 1:
            aux = dict(urllib.parse.parse_qsl(params[1]))
            self.mes = aux
        else:
            aux = dict(urllib.parse.parse_qsl(params[0]))
            self.mes = self.mes | aux
            message = self.mes
        # print(params)
        
        # Sample message:
        # {'mac': '001ec0112232', 'ip': '192.168.001.030', 'soft': '3.4.614',
        # 'model': 'WBB', 'time': '1626793611', 'v1': '226.75', 'v2': '226.75',
        # 'v3': '226.75', 'vt': '226.75', 'i1': '1.71', 'i2': '0.50',
        # 'i3': '1.47', 'it': '3.68', 'p1': '388', 'p2': '113', 'p3': '333',
        # 'pt': '834', 'a1': '277', 'a2': '82', 'a3': '234', 'at': '125',
        # 'r1': '-272', 'r2': '-12', 'r3': '-237', 'rt': '-47', 'q1': '50.04',
        # 'q2': '50.04', 'q3': '50.04', 'qt': '50.04', 'f1': '-0.713',
        # 'f2': '-0.724', 'f3': '0.702', 'ft': '-0.150', 'e1': '4178231',
        # 'e2': '597238', 'e3': '3516927', 'et': '8292396', 'o1': '85060',
        # 'o2': '54608', 'o3': '17337', 'ot': '157006', 't1t': '68.3',
        # 't11': '1.4', 't13': '0.6', 't15': '0.6', 't17': '0.4',
        # 't19': '0.3', 't2t': '0.0', 't21': '0.0', 't23': '0.0', 't25': '0.0',
        # 't27': '0.0', 't29': '0.0', 't3t': '79.4', 't31': '1.2',
        # 't33': '0.5', 't35': '0.6', 't37': '0.4', 't39': '0.3'}
            if 'mac' in message:
                mac = message['mac']
            if 'ip' in message:
                ip = message['ip']
            if 'soft' in message:
                version = message['soft']
            if 'model' in message:
                model = message['model']
            if 'time' in message:
                t = int(message['time'])
                dt = datetime.datetime.fromtimestamp(t).isoformat()
                dt2 = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
            n = datetime.datetime.now()
            now = n.strftime('%Y-%m-%d %H:%M:%S')
            if ip:
                a = ip.split('.')
                ipadd = f'{int(a[0])}.{int(a[1])}.{int(a[2])}.{int(a[3])}'
            self.build_device(mac, ipadd, version, model)
            # Show time and message data
            msg = f'time:"{t}" = "{dt2}" received at "{now}"\nDATA:{message}\n'
            print(msg)
        return

    def eof_received(self):
        """Call when the other end signals it won’t send any more data."""
        logger.info('EOF received!!')
        # self.transport.close()

    def savePacketData(self, message, mac):
        """Save packet data."""
        import os
        import time
        if not mac:
            logger.error('Missing serial number parameter.')
            return
        script_dir = os.path.dirname(__file__)
        rel_path = f'./{mac}_DATA/'
        abs_file_path = os.path.join(script_dir, rel_path)
        timestr = time.strftime('%Y%m%d_%H')
        fname = f'{abs_file_path}datasaved{timestr}.txt'
        try:
            file = open(fname, 'a')
            file.write(str(message) + '\r\n')
            file.close()
        except Exception as e:
            logger.error('Failed saving txt: ' + str(e))

    def connection_lost(self, exc):
        """Call when the connection is lost or closed.

        The argument is an exception object or None (the latter
        meaning a regular EOF is received or the connection was
        aborted or closed).
        """
        logger.warning('Connection lost from {}'.format(self.peername))

    def build_device(self, mac, ip, version, model):
        """Build the list of the device."""
        if not (mac and ip and version and model):
            logger.error(
                f'Missing parameter, need: mac:{mac} '
                f'ip:{ip} version:{version} model:{model}')
            return
        # Add to list this connection
        if mac not in self.devices:
            device = {}
            device['lastconnection'] = 0
            # get Version Device
            device['version'] = version
            device['model'] = model
            device['origen_ip'] = ip
            device['status'] = 0
            self.devices[mac] = device
            logger.debug('Added device ' + mac +
                         ' inside list devices (' +
                         self.ip + ')')
            # Sent to Redis
            if self.useRedis:
                if self.clientRedis:
                    self.clientRedis.set(mac + ':version',
                                        self.devices[mac]['version'])
                    self.clientRedis.set(mac + ':origen_ip',
                                        self.devices[mac]['origen_ip'])
                    # 0 = connected   2 = maybe disconnected   >2 = disconnected
                    status = self.devices[mac]['status']
                    self.clientRedis.set(mac + ':status', status)
                else:
                    logger.critical('Redis is not running or not configured!')

            # thread information that a new device exits
            self.thread.setDevice(self.devices)
        return


class myThreadDisconnect(threading.Thread):
    """Create threads to sockets connections."""

    def __init__(self, threadID, name, device, useRedis):
        """Costructor function."""
        super(myThreadDisconnect, self).__init__()
        # self.shutdown_flag = threading.Event()
        self.shutdown_flag = False
        self.shutdownONLYME_flag = threading.Event()
        self.clientRedis = None
        self.useRedis = useRedis

        # INIT DATA
        self.device = device
        # seconds disconnected
        self.sd = 20

    def setDevice(self, set_device):
        """Set set_device."""
        self.device = set_device

    def setclientRedis(self, set_clientRedis):
        """Set set_clientRedis."""
        self.clientRedis = set_clientRedis

    def stop(self):
        """Stop ALL: stops all thread."""
        self.shutdown_flag = True
        return

    def run(self):
        """Run Listening Socket with Device."""
        while not self.shutdown_flag:
            for i in range(len(self.device)):
                aux = time.perf_counter()
                mac = list(self.device)[i]
                if self.device[mac]['lastconnection'] == 0:
                    self.device[mac]['lastconnection'] = aux
                elapsed = aux - float(self.device[mac]['lastconnection'])
                if elapsed >= self.sd:
                    self.device[mac]['status'] += 0.25
                # 0 = connected   2 = maybe disconnected   >2 = disconnected
                if float(self.device[mac]['status']) == 2.25:
                    if self.useRedis:
                        self.clientRedis.set(mac + ':status', 2.25)
                        logger.warning(f'New desconnection from {mac}')
                time.sleep(0.0001)
            time.sleep(0.25)


class CloudReceiver():
    """Read and get data from Device and manage."""

    def __init__(self):
        """Costructor function."""
        self.listen_IP = '0.0.0.0'
        self.devices = {}
        self.thread = None
        self.modelsPorts = None
        self.loop_TCP = None
        self.server_TCP = None
        self.useRedis = False

    def main(self):
        """Start TCP socket."""
        # start thread
        index = 0
        name = "Thread-" + str(index)
        self.thread = myThreadDisconnect(
            index,
            name,
            self.devices,
            useRedis=self.useRedis)
        self.thread.start()

        # Get ports
        self.modelsPorts = [8600]

        # start server_tcp_socket
        for port in self.modelsPorts:
            logger.debug(f'Starting server TCP on port {port}...')
            self.server_tcp_socket(self.listen_IP, port)

        # run forever
        try:
            self.loop_TCP.run_forever()
        except KeyboardInterrupt:
            msg = 'You pressed Ctrl+C! EXIT, stopping...'
            logger.info(msg)
            # Stop thread
            self.thread.stop()
            # logger.info('Thread stoped.')
        finally:
            # Close the server TCP socket
            if self.server_TCP is not None:
                self.server_TCP.close()
                # logger.info('server_TCP closed')
            # Closing loop TCP socket
            if self.loop_TCP is not None:
                self.loop_TCP.close()
                # logger.info('loop_TCP closed')

    def listensoc(self):
        """Use of ListeningTCPSocket class."""
        return ListeningTCPSocket(self.thread, self.useRedis)

    def server_tcp_socket(self, ip, port):
        """Start TCP listening on specific IP and PORT."""
        # server TCP socket
        # Note: in Python 3.7 need to change next line:
        # From get_event_loop to get_running_loop
        self.loop_TCP = asyncio.get_event_loop()
        # Each client connection will create a new protocol instance
        start_TCP = self.loop_TCP.create_server(lambda: self.listensoc(),
                                                ip,
                                                port)
        try:
            self.server_TCP = self.loop_TCP.run_until_complete(start_TCP)
            aux = self.server_TCP.sockets[0].getsockname()
            logger.info(f'Listening TCP on {aux}')
        except Exception as e:
            logger.error('loop_TCP run_until_complete ' + str(e))
            pass


if __name__ == "__main__":
    """If it's called without imported, this function runs
    because name will be main
    """
    import logging
    import logging.config
    import logging.handlers
    import os
    import datetime
    import time
    LOGGER_LEVEL = logging.DEBUG

    def namer(name):
        """Rename of log file."""
        script_dir = os.path.dirname(__file__)
        rel_path = "./logs/"
        abs_file_path = os.path.join(script_dir, rel_path)

        n = datetime.datetime.now()
        created_at = n.strftime('%Y-%m-%d')
        filename = 'python-' + class_name + '-' + created_at + '.log'
        result = abs_file_path + filename
        return result

    # In which file to save the records?
    script_dir = os.path.dirname(__file__)
    rel_path = "./logs/"
    abs_file_path = os.path.join(script_dir, rel_path)
    class_name = (os.path.basename(__file__)[:-3])
    logfilename = (abs_file_path + 'python-' + class_name + '-RT.log')

    formato_log = ('[%(asctime)s] python.%(levelname)s: %(module)s.py ' +
                   '%(processName)-10s %(funcName)s %(message)s')
    logFormatter = logging.Formatter(formato_log, datefmt='%Y-%m-%d %H:%M:%S')

    # Create the Logger
    handler = logging.handlers.TimedRotatingFileHandler(logfilename,
                                                        when="midnight",
                                                        interval=1)
    handler.setFormatter(logFormatter)
    handler.namer = namer
    logger = logging.getLogger("wibeee")
    logger.addHandler(handler)
    logger.setLevel(LOGGER_LEVEL)

    logger.info(f"LOG INIT {class_name} {__version__}")
    c = CloudReceiver()
    c.main()
    logger.info(f"LOG END {class_name} {__version__}")
