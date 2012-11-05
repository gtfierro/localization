import os
import sys
import re
import subprocess
import shlex
import numpy
import pickle
import time
import redis
from collections import defaultdict
from pprint import pprint
from prun import CmdRun, IOMgr

class Collector:
    """
    Class to mitigate the collection of tcpdump data from several routers to a central source.
    """
 
    def __init__(self, mgr, sample_period, bssids, router_list):
        """
        mgr: IOMgr() from prun.py
        *router_list: list of ip addresses to run tcpdump externally
                      Currently, the Collector class assumes passwordless login as root
        """
        #keep track of processes
        self.routers = {}   #key = router-ip, value = router tcpdump proc
        self.monitors = {}  #key = router-ip, value = monitor proc
        self.macs = {}      #key = router-ip, value = dict of mac addresses to list of detected signals
        self.cycles = {}    #key = router-ip, value = router cycle proc
        self.pings = {}     #key = ping-ip, value = ping proc
        self.records = {}
        self.num_routers = len(list(router_list))

        self.r = redis.StrictRedis()
        self.bssids = bssids

        self.count = 0
        self.mgr = mgr
        self.sample_period = sample_period

        #commands to setup monitoring interface and channel cycling
        cmds = ['/usr/bin/killall tcpdump',
                '/usr/bin/killall sh',
                '/usr/bin/killall ping',
                '/usr/sbin/iw dev wlan0 del',
                '/usr/sbin/iw phy phy0 interface add wlan0 type monitor',
                '/usr/sbin/iw dev wlan0 set txpower fixed 0',
                '/usr/sbin/iw dev wlan0 set channel 4',
                '/sbin/ifconfig wlan0 up']
        setup_procs = {}

        print "Setting up routers..."
        #setup monitoring on routers
        for router in list(router_list):
            cmd = 'ssh root@%s "%s"' % (router, ';'.join(cmds))
            print '  ',cmd
            setup_procs[router] = subprocess.Popen(cmd,shell=True)
#            self.cycles[router] = subprocess.Popen('ssh -o "UserKnownHostsFile /dev/null" root@%s /bin/sh cycle.sh' % router ,shell=True)
            subprocess.call('rm /tmp/%s ; mkfifo /tmp/%s' % (router,router), shell=True)
            print '  ',router,'done!'

        print "Establishing local tcpdump reads..."
        #setup local tcpdump sessions
        for router in list(router_list):
            #cmd = 'tcpdump -tt -e -y IEEE802_11_RADIO -s80 -r /tmp/%s -F router-filter' % router
            cmd = 'tcpdump -ttn -e -y IEEE802_11_RADIO  -r /tmp/%s' % router
            print '  ',cmd
            self.monitors[router] = CmdRun(self.mgr, cmd, self._handle_line, router)
            #setup the dict for each router
            self.macs[router] = defaultdict(list) 
            self.records[router] = defaultdict(list) 
            print "  tcpdump reading from /tmp/%s" % router

        print "Start tcpdump pipe from router to local..."
        #start piping to file
        for router in list(router_list):
            while setup_procs[router].poll() == None:
                time.sleep(.5)
            #cmd = 'ssh root@%s "/usr/sbin/tcpdump -ttn -s80 -e -y IEEE802_11_RADIO -w - -U -i wlan0 " >> /tmp/%s' % (router, router)
            cmd = 'ssh root@%s "/usr/sbin/tcpdump -ttn -e -y IEEE802_11_RADIO -w - -U -i wlan0 " >> /tmp/%s' % (router, router)
            print '  ',cmd
            self.routers[router] = subprocess.Popen(cmd,shell=True)
            #now we can loop through routers.keys() and call .kill()
            print '  Started tcpdump on %s' % router

    def get_all_macs(self,routers=None):
        """
        Returns list of all mac addresses (unique) for all routers specified in [routers], defaults to all routers
        """
        macs = set()
        if isinstance(routers, str):
          routers=list(routers)
        r_iter = routers if routers else self.macs.keys()
        for router in r_iter:
            macs.update(self.macs[router].keys())
        return list(macs)

    def kill(self):
        """
        Safely stops all processes running in separate threads
        """
        for m in self.monitors:
            self.monitors[m].kill()
        for r in self.routers:
            self.routers[r].kill()
        for c in self.cycles:
            self.cycles[c].kill()
        #for p in self.pings:
        #    self.pings[p].kill()

    def clear_data(self):
        """
        Re-initializes internal data structures for records
        """
        for r in self.macs:
            self.macs[r] = defaultdict(list)
        self.count = 0

    def get_data(self,avg=True):
        """
        Returns self.macs, but only mac addressese with at least one third of the sample size packets 
        will be returned. For those that are returned, the median signal is returned
        """
        if avg:
            for router in self.macs:
                for mac in self.macs[router]:
                    self.records[router][mac].extend(self.macs[router][mac])
                    if len(self.macs[router][mac]) >= (.33 * self.sample_period):
                        self.macs[router][mac] = (numpy.median(self.macs[router][mac]), numpy.average(self.macs[router][mac]))
                    else:
                        self.macs[router][mac] = None
            return_dict = {}
            for router in self.macs:
                return_dict[router] = {mac: self.macs[router][mac] for mac in self.macs[router] if self.macs[router][mac]}
            return return_dict
        else:
            return self.macs
    
    def get_data_normalize_to_min(self):
        """
        for all signal strengths s_i, get the min s_min and max s_max, and then with dS = s_max - s_min, recompute each signal strength as
        (s_i - s_min) / dS.
        """
        all_signals = []
        ret = {}
        for router in self.macs:
            for mac in self.macs[router]:
                if self.macs[router][mac]:
                    all_signals.extend(self.macs[router][mac])
        min_signal = min(all_signals) if all_signals else 0
        max_signal = max(all_signals) if all_signals else 0
        delta_signal = float(max_signal - min_signal)
        for router in self.macs:
            ret[router] = {}
            for mac in self.macs[router]:
                if self.macs[router][mac]:
                    #ret[router][mac] = map(lambda x: ((x-min_signal+1) / delta_signal), self.macs[router][mac])
                    ret[router][mac] = map(lambda x: (x-min_signal+1), self.macs[router][mac])
        return ret


    def get_data_for_mac(self, mac, avg=False, datadict=None):
        """
        Returns list of (RSSI, router-ip) tuples, where RSSI is a negative number in dBM indicating signal strength
        and router-ip is the router where that was measured.
        Only returns signals for [mac]
        """
        ret = []
        if not datadict:
            datadict = self.macs
        for router in datadict:
            if datadict[router].has_key(mac):
                if avg: 
                    if datadict[router][mac]:
                        data = numpy.average(datadict[router][mac])
                        ret.append((data, router))
                else:
                    data = datadict[router][mac]
                    ret.extend(zip(data, [router]*len(data)))
            else:
                return None
        return ret


    def _handle_line(self, line,ip='0.0.0.0'):
        """
        Parses line, and if valid, store the signal with the appropriate router and mac address
        """
        line = line.strip()
        bssid = mac = ipaddr = ''
        m = re.search('^(\d+\.\d+).* (-?\d+)dB signal .* TA:([0-9a-f:]+).* Request-To-Send',line)
        if m:
            (time, db, mac) = m.groups()
        else:
            m = re.search('^(\d+\.\d+).* (-?\d+)dB signal(?!.*(?:QoS)).*BSSID:([0-9a-f:]+).*SA:([0-9a-f:]+) ', line)
            if m:
                (time, db, bssid, mac) = m.groups()
        if mac in self.r.smembers('macs'):
            self.macs[ip][mac].append(int(db))
            self.count += 1
