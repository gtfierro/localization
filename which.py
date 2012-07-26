import re
import os
import sys
import numpy as np
import math
import pickle
#import lights
import pygame, sys, os
from pygame.locals import *
from prun import *
from collections import defaultdict
import settings

#for fabric
channels = [11,6,1]
def similarity(tup1, tup2):
    """
    closer to 1.0, the more similar
    """
    a=np.array(map(abs,tup1))
    b=np.array(map(abs,tup2))
    return 1.0 - np.sqrt(np.sum((a-b)**2) / (np.sum(a) * np.sqrt(np.sum(b))))

class Collector:
    def __init__(self, mgr, server, mac, nic = 'wlan0',pos=(0,0)):
        self.power = []
        self.mac = mac
        self.server = server
        self.nic = nic
        self.count = 0
        self.pos = pos
        self.mgr = mgr
        self.channels = [1,6,11]
        self.channel = 0

        cmds = ['/usr/bin/killall -9 tcpdump',
                '/usr/sbin/iw dev wlan0 del',
                '/usr/sbin/iw phy phy0 interface add wlan0 type monitor',
                '/usr/sbin/iw dev wlan0 set txpower fixed 0',
                '/usr/sbin/iw dev wlan0 set channel 11',
                '/sbin/ifconfig wlan0 up']

        self.cmd = 'ssh root@%s "%s; /usr/sbin/tcpdump -tt -l -e -i %s ether src %s"' % (server, ' ; '.join(cmds),  nic, mac)
        print self.cmd
        self.run = CmdRun(mgr, self.cmd, self)

    def restart(self, chan):
        """kills tcpdump, changes channel to [chan], restarts tcpdump"""
        self.run.kill()
        cmds = ['/usr/bin/killall -9 tcpdump',
                '/usr/bin/iw dev wlan0 set channel %s' % chan]
        self.cmd = 'ssh root@%s "%s; /usr/sbin/tcpdump -tt -l -e -i %s ether src %s"' % (self.server, ';'.join(cmds),  self.nic, self.mac)
        print self.cmd
        print 'restarting',self.server,'on channel',chan
        self.run = CmdRun(self.mgr, self.cmd, self)

    def handle_line(self, line):
        line = line.strip()
        m = re.search('^(\d+\.\d+) .* (-?\d+)dB .* SA:([0-9a-f:]+) ', line)
        if m:
            (time, db, mac) = m.groups()
            if not self.mac == mac:
                print "ERROR wrong mac"
            else:
                assert (len(self.power) == 0 or float(time) > self.power[-1][0])
                self.power.append((float(time), int(db)))
                self.count += 1
#        else:
#            print "UNKNOWN RESPONSE (from %s): %s" % (self.server, line)

    def __str__(self):
        return self.server

class Localizer(object):

    def __init__(self,chan=11,graphics=False,mac='f8:0c:f3:1d:16:49',fingerprints_file='fingerprints.db'):
        self.chan = chan
        self.graphics = graphics
        self.mac = mac
        fingerprints = pickle.load(open(fingerprints_file))
        self.mgr = IOMgr()
        self.tmpdict = defaultdict(lambda : defaultdict(list))
        self.collectors = []
        #initialize collectors
        self.add_collector( '128.32.156.131',pos=(285,395))
        self.add_collector( '128.32.156.64', pos=(465,395))
        self.add_collector( '128.32.156.45', pos=(700,350))
        self.add_collector( '128.32.156.67', pos=(900,395))
        #setup collector settings on routers
        #os.system('fab kill_tcpdump')
        #os.system('fab set_monitor')
        #update collector channels
        #os.system('fab set_channel:nic=%s,chan=%s' % ('wlan0',self.chan))

    def add_collector(self, server,pos=(0,0)):
        self.collectors.append(Collector(self.mgr, server, self.mac, pos=pos))

    def interpolate_pos(self, reading):
        """
        reading is a tuple of the readings from collectors A,B,C..
        """
        pos = [0,0]

    def flush(self):
        pickle.dump(self.tmpdict,open('tmpdict.db','wb'))

    def run(self,duration=0,coord=None,loc_index=0):
        start_time = time.time()
        if self.graphics:
            pygame.init()
            screen = pygame.display.set_mode((1088,800))
            floor = pygame.image.load(os.path.join("floor4.png"))
            floor = pygame.transform.scale(floor, (1088,800))

        try:
            last_restart = time.time()
            while True:
                try:
                    self.mgr.poll(1)
                except Exception as e:
                    raise e
                time.sleep(1)
                print
                results = []
                break_now = False
                for c in self.collectors:
                    #set up defaults
                    avg = 0
                    valid_points = [(t,p) for (t,p) in c.power if t >= time.time() - 5]
                    if not valid_points:
                        valid_points = [(t,p) for (t,p) in c.power if t >= time.time() - 10]
                    if not valid_points:
                        results.append( (c.server, float('-inf'), 0 ) )
                    else:
                        l= zip(*valid_points)
                        avg = float(sum(l[1])) / float(len(l[1]))
                        results.append( (c.server,avg,len(valid_points)) )
                print results,'on channel',self.chan
                if len(filter(lambda x: x[1] > float('-inf'),results)) < 1:
                    self.chan = channels[(channels.index(self.chan) + 2) % len(channels)]
                    for c in self.collectors:
                        c.power = []
                        c.restart(self.chan)
                    time.sleep(10)
                    continue
                if coord and loc_index:
                    self.tmpdict[loc_index] = (coord, results)
                if self.graphics:
                    #redraw whole screen
                    for c in self.collectors:
                        pygame.draw.circle(floor, (255,0,0), c.pos, 8)
                    #TODO:draw new dot for position
                    #update draw
                    screen.blit(floor,(0,0))
                    pygame.display.flip()
                #update time
                if duration:
                    if (time.time() - start_time) > duration:
                        return results

        except KeyboardInterrupt:
            for c in l.collectors:
                c.kill()

def track(chan=11,graphics=False,actuate=False):
    print 'On Channel:',chan,'\nUsing Graphics:',graphics
    l = Localizer(chan = chan, graphics = graphics)

    argmax = lambda x: max(x, key=lambda y: y[1])[0]

    last_restart = time.time()
    last_switch = time.time()
    time.sleep(10)
    last = None

    lookup = {}
#    for collector in l.collectors:
#        lookup[collector.mac] = 'Zone' + collector.zone

    while True:
        try:
            closest = argmax(l.run(1))
            print closest
            if actuate:
                print lights.get_level(lookup[closest]),'to',lights.set_level(lookup[closest],3)
                if last:
                    if last != lookup[closest]:
                        print lights.set_level(last,1)
                print lookup[closest], 'now',lights.get_level(lookup[closest])
                last = lookup[closest]

        except KeyboardInterrupt:
            for c in l.collectors:
                c.kill()
            break

def main(graphics=False):
    if len(sys.argv) > 2:
        chan = int(sys.argv[1])
    else:
        chan = 11
    print chan,graphics
    l = Localizer(chan = chan, graphics = graphics)
    l.run(90)

if __name__ == '__main__':
    main()
