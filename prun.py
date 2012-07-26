import pexpect
import os
import select
import time

class IOMgr:
  def __init__(self):
    self.readmap = {}

  def register(self, fd, handler):
    self.readmap[fd] = handler

  def deregister(self,fd):
    self.readmap.pop(fd)

  def poll(self, timeout):
    if not self.readmap:
      return

    while timeout > 0:
      start = time.time()
      rlist, _, _ = select.select(self.readmap.keys(), [], [], timeout)
      for fd in rlist:
        handler = self.readmap[fd]
        handler(fd)

      elapsed = time.time() - start
      timeout = timeout - elapsed

class CmdRun:
  def __init__(self, mgr, cmd, handler):
    self.buf = bytes()
    self.handler = handler
    self.p = pexpect.spawn(cmd)
    self.mgr = mgr
    self.mgr.register(self.p.fileno(), self._handle_data)

  def _handle_data(self, fd):
    try:
        tbuf = os.read(fd, 1024*1024)
    except OSError, e:
        print "Connection closed (%s)" % self.handler
        raise e

    self.buf += tbuf
    pos = self.buf.find('\r\n')
    while pos > -1:
      self.handler.handle_line(self.buf[:pos])
      self.buf = self.buf[pos+2:]
      pos = self.buf.find('\r\n')

  def kill(self):
    self.mgr.deregister(self.p.fileno())
    print self.mgr.readmap,"<-- should be empty"
    self.p.close()
