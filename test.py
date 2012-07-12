import sys
import which
chan = int(sys.argv[1]) if len(sys.argv) > 1 else 1
which.track(chan,False,False)
