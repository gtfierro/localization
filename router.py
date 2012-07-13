from fabric.api import *

class Router:
  """
  Class designed for facilitating sending commands to and reading output from
  an external router running OpenWrt
  """
  def __init__(self, server, mac, nic='wlan0',pos=(0,0)):
    self.server = server
    self.nic = nic
    self.mac = mac
    self.pos = pos

class RouterList:

  def __init__(self, *routers):
    self.routers = routers

  def _run_parallel(fxn):
    res = []
    def run_parallel(self, *args):
      for r in self.routers:
        env.user = 'root'
        env.warn_only = True
        env.host_string = '%s:22' % r.server
        res.append( fxn(self,*args))
      return res.append
    return run_parallel

  @_run_parallel
  def uname(self):
    run('uname',shell=False)

  @_run_parallel
  def kill_tcpdump(self):
    run('killall -9 tcpdump',shell=False)

  def run_tcpdump(self,server,nic,mac):
    env.user = 'root'
    env.warn_only = True
    env.host_string = '%s:22' % server
    #run('nohup tcpdump -tt -l -e -i %s ether src %s >> out.log &' % (nic, mac),shell=False)
    run('/usr/sbin/tcpdump -tt -l -e -i wlan0 >> out.log', shell=False)

  def read_log(self,server):
    run('cat out.log && cat /dev/null > out.log', shell = False)

  @_run_parallel
  def set_channel(self,nic,chan):
    run('/usr/sbin/iw dev %s set channel %d' % (nic, chan), shell=False)

  def cycle_channel(self,nic, cur_chan):
    set_channel(nic, channels[(channels.index(cur_chan) + 1) % len(channels)])


