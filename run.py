import re
import os
import random as rnd
from prun import *

class Collector:
  def __init__(self, mgr, server, mac, nic = 'wlan0'):
    self.power = []
    self.mac = mac
    self.server = server
    self.nic = nic
    self.count = 0
    cmd = 'ssh root@%s "/usr/sbin/tcpdump -tt -l -e -i %s ether src %s"' % (server, nic, mac)
    #cmd = 'ssh root@%s "/usr/sbin/tcpdump -tt -l -e"' % server
    self.run = CmdRun(mgr, cmd, self._handle_line)

  def _handle_line(self, line):
    line = line.strip()
    print line
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
    print cmd
    print os.system(cmd)

def main():
  mgr = IOMgr()
  #mac = '90:27:e4:f6:49:12' #andrew mac
  #mac = '00:26:bb:00:2f:df' #gabe mac
  mac = '0c:df:a4:5e:1b:91' #gabe phone mac
  mac = 'f8:0c:f3:1d:16:49' #andrew verizon mac
  #mac = 'b4:74:9f:c1:2b:dd' #nikita mac
  #mac = '00:26:26:4b:10:8e' #omar mac
  collectors = [
    Collector(mgr, '128.32.156.131', mac),
    Collector(mgr, '128.32.156.64',mac),
    #Collector(mgr, '128.32.156.67',mac),
    #Collector(mgr, 'wrt', mac),
  ]
  try:
    for c in collectors:
      c.set_channel(11)

    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    while True:
      mgr.poll(1)

      ax.clear()
      print [c.count for c in collectors]
      for (c,style) in zip(collectors, ['r.', 'b.']):
        c.count = 0
        if len(c.power) > 2:
          #first = c.power[-1][0] - 3*60
          first = time.time() - 4*60
          c.power = [(t,p) for (t,p) in c.power if t >= first]

          times,powers = zip(*c.power)
          ax.plot(times, powers, style)
      plt.draw()
  except KeyboardInterrupt:
    for c in collectors:
      c.kill()

if __name__ == '__main__':
  main()
