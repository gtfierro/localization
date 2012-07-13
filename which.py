import re
import os
import sys
import numpy as np
import math
import pickle
import lights
import pygame, sys, os
from pygame.locals import *
from prun import *
from collections import defaultdict
from fabric.api import *

#for fabric
channels = [1,6,11]
@parallel
def parallel_uname():
  run('uname',shell=False)

@parallel
def kill_tcpdump():
  run('killall -9 tcpdump',shell=False)

@parallel
def run_tcpdump(nic,mac):
  run('tcpdump -tt -l -e -i %s ether src %s' % (nic, mac),shell=False)

@parallel
def set_channel(nic,chan):
  run('/usr/sbin/iw dev %s set channel %d' % (nic, chan), shell=False)

@parallel
def cycle_channel(nic, cur_chan):
  set_channel(nic, channels[(channels.index(cur_chan) + 1) % len(channels)])

def similarity(tup1, tup2):
  """
  closer to 1.0, the more similar

  """
  a=numpy.array(map(abs,tup1))
  b=numpy.array(map(abs,tup2))
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

  def _handle_line(self, line):
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
    #update collector channels
    for c in self.collectors:
      with settings(warn_only=True,host_string='root@%s' % c.server):
        kill_tcpdump()
        set_channel(c.nic, self.chan)
        #TODO: have this run in the background, have consistent way of reading from it. Make sure we dont' overfill the disk or anything
        #run_tcpdump(c.nic, self.mac)

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
          print e.stacktrace()
          raise e
        time.sleep(1)
        print
        results = []
        for c in self.collectors:

          #last_restart = time.time()
          #if (60 < time.time() - last_restart):
          #  for c in self.collectors:
          #    c.restart()

          #set up defaults
          avg = 0
          valid_points = [(t,p) for (t,p) in c.power if t >= time.time() - 10]
          size = 10 if len(c.power) >= 10 else len(c.power)
          if not valid_points and c.power:
            valid_points = sorted(c.power,key= lambda x: x[0])[:size]
          if not valid_points:
            print "did you run ./monitor on the routers? Also check wireless channel"
            for c in self.collectors:
              c.power = []
              c.cycle_channel()
            time.sleep(15)
            continue
          else:
            l= zip(*valid_points)
            avg = float(sum(l[1])) / float(len(l[1]))
          results.append( (c.server,avg,len(valid_points)) )
        print results,'on channel',self.chan
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
      for c in self.collectors:
        c.kill()

def track(chan=11,graphics=False,actuate=False):
  print chan,graphics
  l = Localizer(chan = chan, graphics = graphics)

  argmax = lambda x: max(x, key=lambda y: y[1])[0]

  last_restart = time.time()
  last_switch = time.time()
  time.sleep(15)
  last = None
  lookup = {'128.32.156.131': 'Zone1',
            '128.32.156.64' : 'Zone2',
            '128.32.156.45' : 'Zone3',
           }
  while True:
    try:
      if (120 < time.time() - last_restart):
        last_restart = time.time()
        for c in l.collectors:
          c.restart()
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
