from prun import CmdRun, IOMgr
import os
import re
from collections import defaultdict

class Collector:
    def __init__(self, mgr, server, channel):
        # Collected data
        self.power = []
        self.macs = defaultdict(list)
        self.count = 0
        self.run = None

        # Config
        self.mgr = mgr
        self.server = server
        self.channel = channel
        self.bssids = ['00:24:14:31:f8:af' , '00:24:14:31:f8:ae' , '00:24:14:31:f6:e4' , '00:24:14:31:f6:e0' , '00:24:14:31:f6:e3' , '00:24:14:31:f9:43' , '00:24:14:31:f6:e1' , '00:24:14:31:f6:e2' , '00:24:14:31:f9:41' , '00:24:14:31:f9:42' , '00:24:14:31:f9:44' , '00:24:14:31:f9:40' , '00:24:14:31:eb:b3' , '00:24:14:31:eb:b1' , '00:24:14:31:eb:b2' , '00:24:14:31:eb:b0' , '00:24:14:31:f8:a3' , '00:24:14:31:f8:a1' , '00:24:14:31:f8:a2' , '00:24:14:31:f8:a4' , '00:24:14:31:f8:a0' , '00:24:14:31:e6:23' , '00:24:14:31:f2:e2' , '00:24:14:31:f2:e4' , '00:24:14:31:e6:21' , '00:24:14:31:e6:22' , '00:24:14:31:e6:24' , '00:24:14:31:e6:20' , '00:24:14:31:f6:ee' , '00:24:14:31:f6:ef' , '00:24:14:31:f9:4e' , '00:24:14:31:f9:4f' , '00:24:14:31:eb:be' , '00:24:14:31:eb:bf' , '00:24:14:31:e6:2e' , '00:24:14:31:e6:2f']
        self.nic = 'wlan0'

    def get_data(self):
        return self.macs

    def clear_data(self):
        self.macs = defaultdict(list)

    def start_channel_cycle(self):
        cmd = 'ssh root@%s "killall -9 sh ; /bin/sh cycle.sh &"' % self.server
        run = CmdRun(self.mgr, cmd, self._handle_line)
        print 'cycling channels on',self.server
        
    def start(self):
        if self.run:
            raise Exception('Controller already running')

        cmds = ['/usr/bin/killall -9 tcpdump',
                '/usr/sbin/iw dev wlan0 del',
                '/usr/sbin/iw phy phy0 interface add wlan0 type monitor',
                '/usr/sbin/iw dev wlan0 set txpower fixed 0',
                '/usr/sbin/iw dev wlan0 set channel %d' % self.channel,
                '/sbin/ifconfig wlan0 up',
                '/usr/sbin/tcpdump -tt -l -e -i %s -y IEEE802_11_RADIO -F /root/router-filter' % self.nic]

        cmd = 'ssh root@%s "%s"' % (self.server, ';'.join(cmds))
        self.run = CmdRun(self.mgr, cmd, self._handle_line)

    def _handle_line(self, line):
        line = line.strip()
        m = re.search('^(\d+\.\d+) .* (-?\d+)dBM antsignal (?!.*(?:QoS)).* BSSID:([0-9a-f:]+).*SA:([0-9a-f:]+) ', line)
        #print line
        if m:
            (time, db, bssid, mac) = m.groups()
            if (int(db) > 0):
                print line
                return
            #default dict will take care of nonexistant macs
            if bssid in self.bssids:
                self.macs[mac].append(int(db))
                self.power.append(int(db))
                self.count += 1

