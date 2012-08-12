import pexpect
import os
import select
import time

class IOMgr:
  def __init__(self):
    self.readmap = {}
    self.ipmap   = {}

  def register(self, fd, handler, ip='0.0.0.0'):
    self.readmap[fd] = handler
    self.ipmap[fd] = ip

  def deregister(self, fd):
    self.readmap.pop(fd)

  def poll(self, timeout):
    if not self.readmap:
      return

    while timeout > 0:
      start = time.time()
      rlist, _, _ = select.select(self.readmap.keys(), [], [], timeout)
      for fd in rlist:
        handler = self.readmap[fd]
        ip = self.ipmap[fd]
        handler(fd,ip)

      elapsed = time.time() - start
      timeout = timeout - elapsed

class CmdRun:
  def __init__(self, mgr, cmd, handle_line, ip='0.0.0.0'):
    self.buf = bytes()
    self.handle_line = handle_line
    self.mgr = mgr
    self.p = pexpect.spawn(cmd)
    self.mgr.register(self.p.fileno(), self._handle_data, ip=ip)

  def _handle_data(self, fd, ip='0.0.0.0'):
    try:
        tbuf = os.read(fd, 1024*1024)
    except OSError, e:
        print "Connection closed"
        raise e

    self.buf += tbuf
    pos = self.buf.find('\r\n')
    while pos > -1:
      self.handle_line(self.buf[:pos],ip)
      self.buf = self.buf[pos+2:]
      pos = self.buf.find('\r\n')

  def kill(self):
    self.mgr.deregister(self.p.fileno())
    self.p.close()
