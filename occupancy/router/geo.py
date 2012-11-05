import os
import sys
import time
import pipe
import Image
import math
import redis
from collections import deque
from collections import defaultdict
from scipy import stats
from prun import IOMgr
import json
import argparse


class Floor(object):
  """
  Geometric representation of a floor. Will keep track of the positions of the routers on the floor
  and provide facilities for performing operations using the router measurements
  """

  def __init__(self, floor_image, collector):
    """
    [floor_image] will be either a file name or a PIL image. All coordinates for internal structures of this
    floor will be relative to the image dimensions. Upper left corner is (0,0).
    [collector] is of class pipe.Collector and serves as the mechanism for getting data
    [macs] is a list of mac address we are tracking
    """
    self.routers = {}
    self.centroid_store = defaultdict(lambda : deque(maxlen=5))
    self.collector = collector
    self.r = redis.StrictRedis() 
    if isinstance(floor_image, str):
      self.floor_image = Image.open(floor_image)    
      self.floor_image_width = self.floor_image.size[0]
      self.floor_image_height = self.floor_image.size[1]
    elif Image.isImageType(floor_image):
      self.floor_image = floor_image
    else:
      raise TypeError('floor_image must be PIL image or filename string')
    
  @property
  def macs(self):
    return self.r.smembers('macs')

  def add_router(self, server, pos):
    """
    Registers router location with Floor instance
    server: router_ip as string
    pos: (x,y) router location relative to floor_image
    """
    if server not in self.collector.routers.keys():
      raise ValueError('router %s must be in collector list' % server)
    self.routers[server] = (pos[0],pos[1])

  def _distance(self, point1, point2):
    """
    Computes the manhattan distance between point1 and point2
    """
    return math.sqrt( (point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

  def _average_points(self, pointlist):
    """
    Computes the average (x,y) point from a list of (x,y) points
    """
    x_coord = sum(map(lambda x: x[0], pointlist)) / float(len(pointlist))
    y_coord = sum(map(lambda x: x[1], pointlist)) / float(len(pointlist))
    return (x_coord,y_coord)
  
  def _filter_n_std_devs(self, n, point_list):
    """
    [point_list] is a list of (distance, (x,y)) tuples. We compute the mean
    of the distances, and then throw out all points that are more than [n]
    standard deviations away from the mean. Returns a list of only the points
    """
    good_points = []
    points = map(lambda x: x[1], point_list)
    if len(points) < 2:
      return points
    scores = list(stats.zscore(map(lambda x: x[0], point_list)))
    for i in xrange(len(scores)):
      if abs(scores[i]) < n:
        good_points.append(points[i])
    return good_points

  def _avg_n_closest_points(self, n, pointlist):
    """
    Return the average of the n closest points out of pointlist
    --
    for each point, compute distance to the other points. Sort them.
    Sum the first n-1 points, take the list with the smallest sum.
    """
    n = max(len(pointlist),n)
    #filter out all null points
    pointlist = filter(lambda x: x != (0,0), pointlist)
    if not pointlist:
      return None
    point_dict = {}
    sum_dict = {}
    for p in pointlist:
      other_points = filter(lambda x: x!=p, pointlist)
      dist_to_points = map(lambda x: (self._distance(x,p), x),other_points)
      point_dict[p] = sorted(dist_to_points, key = lambda x: x[0]) # sort by distance
      sum_dict[p] = sum(map(lambda x: x[0], point_dict[p][:n-1]))
    min_sum_point = min(sum_dict, key=lambda x: sum_dict[x])
    points = self._filter_n_std_devs(1.5, point_dict[p][:n-1])
    points.append(min_sum_point)
    return self._average_points(points)

  def compute_centroid_exp(self,mac, data):
    """
    Computes the (x,y) position of the centroid given [data]. Converts dBM into linear scale
    [data] is a list of tuples (RSSI, router-ip), where RSSI is a negative number in dBM
    and router-ip is a string corresponding to one of the routers we've registered with
    this Floor
    """
    x_coord = 0
    y_coord = 0
    if not data:
        return x_coord, y_coord
    sum_signals = sum(map(lambda x: .001 * (10 ** (float(x[0]) / 10.0)), data))
    for point in data:
      signal = .001 * (10 ** (float(point[0]) / 10.0))
      if point[1] not in self.routers.keys():
        continue
      weight = signal / sum_signals
      x_coord += ( self.routers[point[1]][0] * weight )
      y_coord += ( self.routers[point[1]][1] * weight )
    self.centroid_store[mac].append((x_coord,y_coord))
    return x_coord, y_coord

  def compute_centroid_lin(self, mac, data):
    """
    Computes the (x,y) position of the centroid given [data]. Converts dBM into linear scale
    [data] is a list of tuples (RSSI, router-ip), where RSSI is a negative number in dBM
    and router-ip is a string corresponding to one of the routers we've registered with
    this Floor
    """
    sum_signals = sum(map(lambda x: x[0], data))
    x_coord = 0
    y_coord = 0
    for point in data:
      signal = float(point[0])
      if point[1] not in self.routers.keys():
        continue
      weight = signal / sum_signals
      x_coord += ( self.routers[point[1]][0] * weight )
      y_coord += ( self.routers[point[1]][1] * weight )
    self.centroid_store[mac].append((x_coord,y_coord))
    return x_coord, y_coord

  def get_centroid(self, mac):
    """
    returns the centroid for a given mac address
    """
    # get the most recent data for the given mac address
    alldata = self.collector.get_data_normalize_to_min()
    macdata = self.collector.get_data_for_mac(mac, True, datadict=alldata)
    # compute the centroid from the recent data
    self.compute_centroid_exp(mac,macdata)
    # use self.centroid_store historical data
    res = self._avg_n_closest_points(5, self.centroid_store[mac])
    if res:
        print macdata
        d = {}
        d['x'] = res[0]
        d['y'] = res[1]
        d['ip'] = self.r.hget('macip', mac)
        if macdata:
            d['last_updated'] = int(time.time())
        else:
            old_data = self.r.hget('client_location',mac)
            if old_data:
                d['last_updated'] = int(json.loads(old_data)['last_updated'])
            else:
                return None
        self.r.hset('client_location',mac, json.dumps(d))
        if abs(d['last_updated'] - int(time.time())) > 60:
            return None
    return res 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--sample-period',type=int,default=10,help='seconds to sample in between updating')
    parser.add_argument('-g','--enable-graphics',action='store_true',default=False,help='true if you want to display pygame graphics')
    parser.add_argument('config_file',type=str,help='''specify the config file containing the routers. Format:\nrouter-mac router-ip x y''')
    args = parser.parse_args()

    router_ips = []
    bssids = []
    coords = []
    mgr = IOMgr()
    with open(args.config_file,'r') as f:
        #loop through config file
        for line in f.readlines():
            if not line or line.startswith('#'):
                continue
            if line.startswith('router'):
                router_ips.append(line.split()[2]) 
                coords.append(map(int,line.split()[-2:]))
            elif line.startswith('bssid'):
                bssids.append(line.split()[0])
    # create Collector
    c = pipe.Collector(mgr, args.sample_period, bssids, router_ips)
    # create Floor
    floor = Floor('floor4.png',c)
    # add routers
    for router,coord in zip(router_ips,coords):
        floor.add_router(router, coord)

    if args.enable_graphics:
        print "#" * 24
        print "#Using Pygame graphics!#"
        print "#" * 24
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((600,240))
        fl = pygame.image.load(os.path.join('floor4.png'))
        fl = pygame.transform.scale(fl, (600,240))
        screen.blit(fl,(0,0))
    while True:
      try:
        time.sleep(args.sample_period)
        mgr.poll(args.sample_period)
        centroids = []
        for mac in floor.macs:
          cent = floor.get_centroid(mac)
          if cent:
              print mac
              print cent
              centroids.append(cent)
          else:
              print 'deleting mac: ',mac
              floor.r.hdel('client_location',mac)
        print '-'*20
        if args.enable_graphics:
            screen.blit(fl,(0,0))
            for mac in floor.macs:
              print floor.centroid_store[mac]
              for cen in floor.centroid_store[mac]:
                pygame.draw.circle(screen, (0,255,0), map(lambda x: int(x), list(cen)), 5)
            for cen,col in zip(centroids, [(255,0,0),(0,255,0),(0,0,255),(255,255,0)]):
              if cen:
                pygame.draw.circle(screen, col, map(lambda x: int(x), cen), 5)
            pygame.display.flip()
        c.clear_data()
      except KeyboardInterrupt:
        c.kill()
        sys.exit(0)

if __name__=="__main__":
    main()
