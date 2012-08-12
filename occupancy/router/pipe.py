import os
import sys
import re
import subprocess
import shlex
import numpy
import pickle
from collections import defaultdict
from pprint import pprint
from prun import CmdRun, IOMgr

class Collector:
    """
    Class to mitigate the collection of tcpdump data from several routers to a central source.
    """
  
    def __init__(self, mgr, sample_period, *router_list):
        """
        mgr: IOMgr() from prun.py
        *router_list: list of ip addresses to run tcpdump externally
                      Currently, the Collector class assumes passwordless login as root
        """
        #keep track of processes
        self.routers = {}   #key = router-ip, value = router tcpdump proc
        self.monitors = {}  #key = router-ip, value = monitor proc
        self.macs = {}      #key = router-ip, value = dict of mac addresses to list of detected signals

        self.count = 0
        self.mgr = mgr
        self.sample_period = sample_period

        #commands to setup monitoring interface and channel cycling
        cmds = ['/usr/bin/killall tcpdump',
                '/usr/bin/killall sh',
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
            print '  ',cmd_string
            subprocess.call(cmd_string,bufsize=1,shell=True)
            subprocess.call('rm /tmp/%s ; mkfifo /tmp/%s' % (router,router), shell=True)
            print '  ',router,'done!'

        print "Establishing local tcpdump reads..."
        #setup local tcpdump sessions
        for router in list(router_list):
            cmd = 'tcpdump -tt -e -y IEEE802_11_RADIO -s80 -r /tmp/%s' % router
            print '  ',cmd
            self.monitors[router] = CmdRun(self.mgr, cmd, self._handle_line, router)
            #setup the dict for each router
            self.macs[router] = defaultdict(list) 
            print "  tcpdump reading from /tmp/%s" % router

        print "Start tcpdump pipe from router to local..."
        #start piping to file
        for router in list(router_list):
            cmd = 'ssh root@%s "/usr/sbin/tcpdump -e -y IEEE802_11_RADIO -w - -U -i wlan0 -F /root/router-filter" >> /tmp/%s' % (router, router)
            print '  ',cmd
            self.routers[router] = subprocess.Popen(cmd,shell=True)
            #now we can loop through routers.keys() and call .kill()
            print '  Started tcpdump on %s' % router

    def kill(self):
        for m in self.monitors:
            self.monitors[m].kill()
        for r in self.routers:
            self.routers[r].kill()

    def clear_data(self):
        self.power = []
        for r in self.macs:
            self.macs[r] = defaultdict(list)
        self.count = 0


    def get_data(self):
        """
        Returns self.macs, but only mac addressese with at least one third of the sample size packets
        will be returned. For those that are returned, the median signal is returned
        """
        for router in self.macs:
            for mac in self.macs[router]:
                if len(self.macs[router][mac]) >= (.33 * self.sample_period):
                    self.macs[router][mac] = numpy.median(self.macs[router][mac])
                else:
                    self.macs[router][mac] = None
        return_dict = {}
        for router in self.macs:
            return_dict[router] = {mac: self.macs[router][mac] for mac in self.macs[router] if self.macs[router][mac]}
        return return_dict

    #TODO: filter by mac addresses that have more than 100 readings?
    #TODO: finish up the math
    
    def _handle_line(self, line,ip='0.0.0.0'):
        line = line.strip()
        m = re.search('^(\d+\.\d+).* (-?\d+)dB signal(?!.*(?:QoS)).*SA:([0-9a-f:]+) ', line)
        if m:
            (time, db, mac) = m.groups()
            self.macs[ip][mac].append(int(db))
            self.count += 1

def main(sample_period):
    mgr = IOMgr()
    c = Collector(mgr,sample_period,"128.32.156.64","128.32.156.67")
    while True:
        try:
            mgr.poll(sample_period)
            print c.get_data()
            pickle.dump(c.macs,open('macs.db','wb'))
            c.clear_data()
        except KeyboardInterrupt:
            c.kill()
            sys.exit(0)

if __name__=="__main__":
    main(10)
