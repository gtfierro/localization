from collector import Collector
from prun import IOMgr
import numpy
import time
import json

class Localizer:
    def __init__(self, search_mac = 'f8:0c:f3:1d:16:49', channels = [11,6,1]):
        self.mgr = IOMgr()
        self.search_mac = search_mac
        self.channels = channels
        self.chan_idx = 0

        self.collectors = []
        
        self._add_collector('128.32.156.131')
        self._add_collector('128.32.156.64')
        self._add_collector('128.32.156.45')
        self._add_collector('128.32.156.67')

    def _add_collector(self, ip):
        self.collectors.append(Collector(self.mgr, ip, self.search_mac, self.channels[self.chan_idx]))

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

    def _median_signals(self):
        medians = []
        counts = []
        for c in self.collectors:
            data = c.get_data()
            c.clear_data()

            counts.append(len(data))
            if len(data) == 0:
                medians.append(float('-inf'))
            else:
                data = map(lambda x: x[1], data)
                medians.append(data[len(data) / 2])
        return (medians, counts)

    def run(self):
        for c in self.collectors:
            c.start()
        # Timeout to start tcpdump
        time.sleep(3)

        while True:
            # Sample for n seconds
            self.mgr.poll(3)
            (medians, counts) = self._median_signals()
            zone = medians.index(max(medians))+1
            #(avgs, counts) = self._average_signals()
            #zone = avgs.index(max(avgs))+1
            with open('../demo/zone.json','wb') as f:
              d = {'zone': zone+1}
              json.dump(d,f)
            #print zone+1, avgs
            print zone+1, medians

if __name__ == '__main__':
    l = Localizer()
    l.run()
