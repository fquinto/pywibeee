#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AUTHOR    | DATE       | VERSION | COMMENTS
# F.Quinto  | 2021-11-03 | 0.0.0   | First draft

__version__ = "0.0.0"
"""Wibeee sender (emulator)."""
import httpx

class WiBeeeEmulator():
    """WiBeeeEmulator class."""

    def __init__(self):
        """First init class."""
        self.destinations = [
            'wibeee.circutor.com:8080',
            'wattius.mirubee.com:8600',
            'wattius.mirubee.com:8080',
            'datosmonitorconsumo.iberdrola.es:8080',
            'wibeee.smilics.com:8080'
        ]
        self.mac = '001ec0112232'
        self.ip = '192.168.001.150'

    def randomModel(self):
        """Return a random model."""
        import random
        # WBM = Wibeee 1Ph
        # WBT = Wibeee 3Ph
        # WMX = Wibeee MAX
        # WTD = Wibeee 3Ph RN
        # WX2 = Wibeee MAX 2S
        # WX3 = Wibeee MAX 3S
        # WXX = Wibeee MAX MS
        # WBB = Wibeee BOX
        # WB3 = Wibeee BOX S3P
        # W3P = Wibeee 3Ph 3W
        # WGD = Wibeee GND
        # WBP = Wibeee SMART PLUG
        models = [
            'WBM',
            'WBT',
            'WMX',
            'WTD',
            'WX2',
            'WX3',
            'WXX',
            'WBB',
            'WB3',
            'W3P',
            'WGD',
            'WBP'
        ]
        return random.choice(models)

    def randomVoltage(self):
        """Return a random voltage."""
        return self.randomValues(230, 236)

    def randomIntensity(self):
        """Return a random intensity."""
        return self.randomValues(0.17, 0.75)

    def randomPower(self):
        """Return a random power."""
        return self.randomValues(39, 250)

    def randomValues(self, a, b):
        """Return a random values between floats."""
        import random
        return str(round(random.uniform(a, b), 2))
    
    def startingloop(self):
        """Start loop."""
        import time
        while True:
            self.main()
            time.sleep(5)

    def main(self):
        """Main function."""
        import datetime
        n = datetime.datetime.now()
        timestamp = int(datetime.datetime.timestamp(n))
        for host in self.destinations:
            url = f'http://{host}/Wibeee/receiverAvg'
            params = {
                'mac': self.mac,
                'ip': self.ip,
                'soft': '3.4.000',
                'model': 'WBB',
                # 'time': '1585817562',
                'time': timestamp,
                'v1': self.randomVoltage(),
                'v2': self.randomVoltage(),
                'v3': self.randomVoltage(),
                'vt': self.randomVoltage(),
                'i1': self.randomIntensity(),
                'i2': self.randomIntensity(),
                'i3': self.randomIntensity(),
                'it': self.randomIntensity(),
                'p1': self.randomPower(),
                'p2': self.randomPower(),
                'p3': self.randomPower(),
                'pt': self.randomPower(),
                'a1': '43',
                'a2': '0',
                'a3': '0',
                'at': '42',
                'r1': '0',
                'r2': '0',
                'r3': '0',
                'rt': '0',
                'q1': '50.20',
                'q2': '50.20',
                'q3': '50.20',
                'qt': '50.20',
                'f1': '0.528',
                'f2': '0.000',
                'f3': '-0.003',
                'ft': '0.240',
                'e1': '111',
                'e2': '2392',
                'e3': '1006',
                'et': '3509',
                'o1': '0',
                'o2': '0',
                'o3': '0',
                'ot': '0',
                'pcs': '123',
                't1t': '0.0',
                't11': '0.0',
                't13': '0.0',
                't15': '0.0',
                't17': '0.0',
                't19': '0.0',
                't2t': '0.0',
                't21': '0.0',
                't23': '0.0',
                't25': '0.0',
                't27': '0.0',
                't29': '0.0',
                't3t': '0.0',
                't31': '0.0',
                't33': '0.0',
                't35': '0.0',
                't37': '0.0',
                't39': '0.0'
            }
            print(f'Testing url: {url}')
            r = httpx.get(url, params=params)
            print(r.status_code)
            print(r.text)
            print(r.url)


if __name__ == "__main__":
    """Main function."""
    wibeee_sender = WiBeeeEmulator()
    wibeee_sender.startingloop()
