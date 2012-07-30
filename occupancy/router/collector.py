from prun import CmdRun, IOMgr
import os
import re
from collections import defaultdict

class Collector:
    def __init__(self, mgr, server, channel):
        # Collected data
        self.power = []
        self.macs = defaultdict(list)
        self.owned_macs = [] #list of mac addresses actually in the zone
        self.count = 0
        self.run = None

        # Config
        self.mgr = mgr
        self.server = server
        self.channel = channel
        self.nic = 'wlan0'

    def get_data(self):
        return self.macs, self.power

    def clear_data(self):
        self.power = []
        self.macs = defaultdict(list)

    def start_channel_cycle(self):
        cmd = 'ssh root@%s "killall -9 sh ; sh cycle.sh &"' % self.server
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
        m = re.search('^(\d+\.\d+) .* (-?\d+)dB .* SA:([0-9a-f:]+) ', line)
        if m:
            (time, db, mac) = m.groups()
            assert (len(self.power) == 0 or float(time) > self.power[-1][0])
            #default dict will take care of nonexistant macs
            self.macs[mac].append(int(db))
            self.power.append((float(time), int(db)))
            self.count += 1

