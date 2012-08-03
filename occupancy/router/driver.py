from collector import Collector
from prun import IOMgr
from collections import defaultdict
import numpy
import time
import json
import sys

class Localizer:
    def __init__(self, channels = [1,6,11]):
        self.mgr = IOMgr()
        self.channels = channels
        self.chan_idx = 0

        self.collectors = []
        
        self._add_collector('128.32.156.131')
        self._add_collector('128.32.156.64')
        self._add_collector('128.32.156.45')
        self._add_collector('128.32.156.67')

    def _add_collector(self, ip):
        self.collectors.append(Collector(self.mgr, ip, self.channels[self.chan_idx]))

    def _average_signals(self):
        avgs = []
        counts = []
        for c in self.collectors:
            data = c.get_data()
            c.clear_data()

            counts.append(len(data))
            if len(data) == 0:
                avgs.append(float('-inf'))
            else:
                avgs.append(numpy.mean(data, 0)[1])
        return (avgs, counts)

    def _median(self, data):
      if len(data) == 0:
        return float('-inf')
      if numpy.median(data) > 0:
        print data
      return numpy.median(data)

    def _median_signals(self):
        medians = []
        counts = []

        for c in self.collectors:
            data = c.get_data()
            c.clear_data()

            counts.append(len(data))
            data = map(lambda x: x[1], data)
            medians.append(self._median(data))
        return (medians, counts)

    def _get_occupancy(self):
        collector_macs = defaultdict(lambda : defaultdict(lambda : [float('-inf')]))
        owned_macs = defaultdict(list)
        all_macs = set()

        for c in self.collectors:
            macs = c.get_data() #tuple of c.mac
            all_macs.update(set(macs))
            c.clear_data()
            for mac in macs:
                collector_macs[c.server][mac] = self._median(macs[mac])
        for mac in all_macs:
            owner = max( [(collector_macs[c.server][mac], c.server)  for c in self.collectors] , key=lambda x: x[0])[1]
            #print mac,':',[(collector_macs[c.server][mac], c.server)  for c in self.collectors], owner
            owned_macs[owner].append(mac)
        return owned_macs


    def run(self,graphics=False):
        for c in self.collectors:
            c.start_channel_cycle()
        for c in self.collectors:
            c.start()
        # Collect packets over sample_period seconds
        sample_period = 60

        time.sleep(sample_period) # Initialization time

        # No data for last no_data_count seconds 
        no_data_count = 0
        if graphics:
            import matplotlib
            matplotlib.use('TkAgg')
            import matplotlib.pyplot as plt
            plt.ion()
            fig = plt.figure()
            ax = fig.add_subplot(111)

        timestamp = 0
        while True:
            # Sample for n seconds
            self.mgr.poll(sample_period)
            owned_macs = self._get_occupancy()
            if graphics:
              timestamp += sample_period
              for (s,style) in zip(owned_macs,['r.','b.','g.','c.']):
                  ax.plot(timestamp, len(owned_macs[s]), style)
              plt.draw()
            print [(c, len(owned_macs[c])) for c in owned_macs]

if __name__ == '__main__':
    l = Localizer()
    graphics = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    l.run(graphics)
