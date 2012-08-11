from prun import CmdRun, IOMgr
import subprocess
import shlex
import os
import sys
import re
from collections import defaultdict

class Collector:
  
    def __init__(self, mgr, *router_list):
        #keep track of processes
        self.routers = {}
        self.monitors = {}

        #data
        self.power = []
        self.macs = defaultdict(list)
        self.count = 0
        self.mgr = mgr

        cmds = ['/usr/bin/killall -9 tcpdump',
                '/usr/sbin/iw dev wlan0 del',
                '/usr/sbin/iw phy phy0 interface add wlan0 type monitor',
                '/usr/sbin/iw dev wlan0 set txpower fixed 0',
                '/usr/sbin/iw dev wlan0 set channel 1',
                '/sbin/ifconfig wlan0 up',
                '/bin/sh cycle.sh &']

        print "Setting up routers..."
        #setup monitoring on routers
        for router in list(router_list):
            cmd_string = 'ssh root@%s "%s"' % (router, ';'.join(cmds))
            subprocess.call(cmd_string,bufsize=1,shell=True)
            subprocess.call('rm /tmp/%s ; mkfifo /tmp/%s' % (router,router), shell=True)
            print router,'done!'

        #setup local tcpdump sessions
        for router in list(router_list):
          cmd = 'tcpdump -r /tmp/%s' % router
          self.monitors[router] = CmdRun(self.mgr, cmd, self._handle_line)

        print "Start tcpdump pipe from router to local machine..."
        #start piping to file
        for router in list(router_list):
            cmd = 'ssh root@%s "/usr/sbin/tcpdump -tt -e -w - -U -i wlan0 -y IEEE802_11_RADIO" >> /tmp/%s' % (router, router)
            print cmd
            self.routers[router] = subprocess.Popen(cmd,shell=True)
            #now we can loop through routers.keys() and call .kill()

    
    def _handle_line(self, line):
        line = line.strip()
        m = re.search('^(\d+\.\d+) .* (-?\d+)dBM antsignal (?!.*(?:QoS)).* BSSID:([0-9a-f:]+).*SA:([0-9a-f:]+) ', line)
        print line
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

