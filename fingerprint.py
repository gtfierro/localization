"""
@author Gabe Fierro

Library for logging/using RSSI fingerprinting
"""
import sys
import os
import re
import logging
import pickle
import time
from collections import defaultdict

class RSSIReader(object):
  """
  Reads off the SSID/MAC/RSSI of networks around you at the provided sample rate
  and stores them in a pickle file for later usage
  """

  def __init__(self, sample_rate, log_dest='rssi.db', opsys=None,server=None):
    """
    [sample_rate]: in seconds, the time between getting an RSSI fingerprint
    [log_dest]: the location/name of the rssi db file, defaults to 'rssi.db'
    [opsys]: the operating system of this computer, defaults to None, but
              we try to figure it out for you
    [server]: the remote server to connect to (optional)
    """
    self.sample_rate = sample_rate
    self.log_dest = log_dest
    self.server = server
    if not opsys:
      host = os.uname()
      if 'Darwin' in host:
        print 'Using Mac OS X'
        self.opsys = 'mac'
      elif 'Linux' in host:
        print 'Using Linux'
        self.opsys = 'linux'
    else:
      self.opsys = opsys

  def get_rssi_fingerprint(self):
    """
    Depending on the operating system, gets the RSSI fingerprint, formats it
    and appends it to the self.log_dest file
    """
    ret_list = []

    if self.opsys == 'mac':
      base = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/A/Resources/airport -s"
      res = os.popen(base)
      results = res.readlines()[1:]
      get_mac = lambda x: re.search('([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])',x).group()
      get_rssi = lambda x: re.search('-[0-9]{2}',x).group()
      get_ssid = lambda x: x[:x.index(get_mac(x))].strip()
      for r in results:
        mac = get_mac(r)
        rssi = float(get_rssi(r))
        print mac,rssi
        ret_list.append((mac,rssi))
    elif self.opsys == 'linux':
      if self.server:
        print 'remote'
        base = 'ssh root@%s iw wlan0 scan' % (self.server)
      else:
        base = 'iw wlan0 scan'
      results = os.popen(base)
      print base
      results = ''.join(results.readlines())
      get_mac = lambda x: re.search('([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])',x).group()
      get_rssi = lambda x: re.search('-[0-9]{2}',x).group()
      for r in results.split('last')[:-1]:
        r=' '.join(r.split())
        mac = get_mac(r)
        rssi = float(get_rssi(r))
        print mac,rssi
        ret_list.append((mac,rssi))
    return ret_list

  def start_sampling(self,duration=None,number=None):
    """
    Starts sampling using get_rssi_fingerprint every [sample_rate] seconds and sends the results
    to [log_dest]. Gets results for [duration] seconds or gets [number] results, whichever comes
    first. Leave both arguments blank to sample for forever.
    """
    #collect samples
    start_time = time.time()
    samples = {}
    time.sleep(self.sample_rate)
    while 1:
      tuples  = self.get_rssi_fingerprint()
      current_time = time.mktime(time.localtime())
      samples[current_time] = tuples
      if number:
        if len(samples) >= number:
          break
      if duration:
        if (time.time() - start_time) > duration:
          break
      time.sleep(self.sample_rate)

    #consolidate samples
    averages = defaultdict(list)
    for s in samples:
      for atom in samples[s]:
        averages[atom[0]].append(atom[1])

    #average rssi per MAC address
    for s in averages:
      averages[s] = sum(averages[s]) / float(len(averages[s]))

    print averages
    #store samples
    with open(self.log_dest,'wb') as fout:
      pickle.dump(averages, fout)


