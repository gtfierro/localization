import re
import os
import sys
import random as rnd
from prun import *

class Collector:
  def __init__(self, mgr, server, mac, nic = 'wlan0'):
    self.power = []
    self.mac = mac
    self.server = server
    self.nic = nic
    self.count = 0
    #print os.system('ssh root@%s /bin/sh monitor' % (server))
    cmd = 'ssh root@%s "/usr/sbin/tcpdump -tt -l -e -i %s ether src %s"' % (server, nic, mac)
    #cmd = 'ssh root@%s "/usr/sbin/tcpdump -tt -l -e"' % server
    self.run = CmdRun(mgr, cmd, self._handle_line)

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

  def set_channel(self, chan):
    cmd = 'ssh root@%s "/usr/sbin/iw dev %s set channel %d"' % (self.server, self.nic, chan)
    print cmd
    print os.system(cmd)

  def kill(self):
    self.run.kill()
    cmd = 'ssh root@%s "/usr/bin/killall -9 tcpdump"' % self.server
    print os.system(cmd)

def main():
  mgr = IOMgr()
  if len(sys.argv) > 1:
    chan = int(sys.argv[1])
  else:
    chan = 11
  #mac = '90:27:e4:f6:49:12' #andrew mac
  #mac = '00:26:bb:00:2f:df' #gabe mac
  mac = '0c:df:a4:5e:1b:91' #gabe phone mac
  #mac = 'b4:74:9f:c1:2b:dd' #nikita mac
  #mac = '00:26:26:4b:10:8e' #omar mac
  #mac = '00:0d:f0:8d:ef:80' #fitpc mac
  #mac = '58:55:CA:7s:2A:93' #gabe ipod mac
  collectors = [
    Collector(mgr, '128.32.156.131', mac),
    Collector(mgr, '128.32.156.64',mac),
 #   Collector(mgr, '128.32.156.67',mac),
  ]

  try:
    for c in collectors:
      c.set_channel(chan)

    while True:
      mgr.poll(1)
      time.sleep(1)
      closest = float('inf') #infinity
      print
      for c in collectors:
        print c.server,
        if not c.power:
          print "did you run ./monitor on the routers?"
        c.count = 0
        if len(c.power) > 2:
          first = time.time() - 4*60
          c.power = [(t,p) for (t,p) in c.power if t >= first]
          l= zip(*c.power)
          avg = float(sum(l[1])) / float(len(l[1]))
          print avg
  except KeyboardInterrupt:
    for c in collectors:
      c.kill()

if __name__ == '__main__':
  main()

