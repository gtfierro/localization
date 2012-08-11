import pipe
from prun import IOMgr
mgr = IOMgr()
c = pipe.Collector(mgr,"128.32.156.64","128.32.156.67")

while True:
    mgr.poll(4)
    print c.macs
