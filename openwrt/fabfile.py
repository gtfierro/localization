from fabric.api import *

env.user = 'root'
env.hosts = ['128.32.156.45', '128.32.156.64', '128.32.156.67', '128.32.156.131']
env.warn_only = True

@parallel
def reset():
  run('reboot',shell=False)

@parallel
def uname():
  run('uname',shell=False)

@parallel
def kill_tcpdump():
  run('/usr/bin/killall -9 tcpdump',shell=False)

@parallel
def set_monitor():
  run('/usr/sbin/iw dev wlan0 del',shell=False)
  run('/usr/sbin/iw phy phy0 interface add wlan0 type monitor',shell=False)
  run('/usr/sbin/iw dev wlan0 set txpower fixed 0',shell=False)
  run('/sbin/ifconfig wlan0 up',shell=False)

@parallel
def set_channel(nic='nic',chan='chan'):
  chan=int(chan)
  run('/usr/sbin/iw dev %s set channel %d' % (nic, chan), shell=False)
