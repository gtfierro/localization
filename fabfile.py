from fabric.api import *

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
  run('iw dev %s set channel %d' % (nic, chan), shell=False)
