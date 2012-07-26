from prun import CmdRun, IOMgr
import re

class Collector:
    def __init__(self, mgr, server, search_mac, channel):
        # Collected data
        self.power = []
        self.count = 0
        self.run = None

        # Config
        self.mgr = mgr
        self.server = server
        self.search_mac = search_mac
        self.channel = channel
        self.nic = 'wlan0'

    def get_data(self):
        return self.power

    def clear_data(self):
        self.power = []

    def set_channel(self, channel):
        self.channel = channel
        if self.run:
            self.run.kill()
            self.run = None
       
        cmds = ['/usr/bin/killall -9 tcpdump',
               '/usr/sbin/iw dev wlan0 set channel %d' % self.channel,
               '/usr/sbin/tcpdump -tt -l -e -i %s ether src %s' % (self.nic, self.search_mac)]
        cmd = 'ssh root@%s "%s"' % (self.server, ';'.join(cmds))
        self.run = CmdRun(self.mgr, cmd, self._handle_line)

    def start(self):
        if self.run:
            raise Exception('Controller already running')

        cmds = ['/usr/bin/killall -9 tcpdump',
                '/usr/sbin/iw dev wlan0 del',
                '/usr/sbin/iw phy phy0 interface add wlan0 type monitor',
                '/usr/sbin/iw dev wlan0 set txpower fixed 0',
                '/usr/sbin/iw dev wlan0 set channel %d' % self.channel,
                '/sbin/ifconfig wlan0 up',
                '/usr/sbin/tcpdump -tt -l -e -i %s ether src %s' % (self.nic, self.search_mac)]

        cmd = 'ssh root@%s "%s"' % (self.server, ';'.join(cmds))
        self.run = CmdRun(self.mgr, cmd, self._handle_line)

    def _handle_line(self, line):
        line = line.strip()
        m = re.search('^(\d+\.\d+) .* (-?\d+)dB .* SA:([0-9a-f:]+) ', line)
        if m:
            (time, db, mac) = m.groups()
            if not self.search_mac == mac:
                print "ERROR wrong mac"
            else:
                assert (len(self.power) == 0 or float(time) > self.power[-1][0])
                self.power.append((float(time), int(db)))
                self.count += 1
        else:
            print "UNKNOWN RESPONSE (from %s): %s" % (self.server, line)

