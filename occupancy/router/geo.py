import os
import sys
import time
import pipe
import Image
#import sympy
#from sympy.geometry import Point
from prun import IOMgr


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
    """
    self.routers = {}
    self.centroid_store = {}
    self.collector = collector

    if isinstance(floor_image, str):
      self.floor_image = Image.open(floor_image)    
      self.floor_image_width = self.floor_image.size[0]
      self.floor_image_height = self.floor_image.size[1]
    elif Image.isImageType(floor_image):
      self.floor_image = floor_image
    else:
      raise TypeError('floor_image must be PIL image or filename string')


  def add_router(self, server, pos):
    """
    Registers router location with Floor instance
    server: router_ip as string
    pos: (x,y) router location relative to floor_image
    """
    if pos[0] > self.floor_image_width or pos[0] < 0:
      raise ValueError('x pos must be within %d and 0' % self.floor_image_width)
    if pos[1] > self.floor_image_height or pos[1] < 0:
      raise ValueError('y pos must be within %d and 0' % self.floor_image_height)
    if server not in self.collector.routers.keys():
      raise ValueError('router %s must be in collector list' % server)
    self.routers[server] = (pos[0],pos[1])


  def compute_centroid_exp(self, data):
    """
    Computes the (x,y) position of the centroid given [data]. Converts dBM into linear scale
    [data] is a list of tuples (RSSI, router-ip), where RSSI is a negative number in dBM
    and router-ip is a string corresponding to one of the routers we've registered with
    this Floor
    """
    sum_signals = sum(map(lambda x: .001 * (10 ** (float(x[0]) / 10.0)), data))
    x_coord = 0
    y_coord = 0
    for point in data:
      signal = .001 * (10 ** (float(point[0]) / 10.0))
      #print signal, point[0]
      if point[1] not in self.routers.keys():
        continue
      weight = signal / sum_signals
      x_coord += ( self.routers[point[1]][0] * weight )
      y_coord += ( self.routers[point[1]][1] * weight )
    return (x_coord, y_coord)

  def compute_centroid(self, data):
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
      #print signal, point[0]
      if point[1] not in self.routers.keys():
        continue
      weight = signal / sum_signals
      x_coord += ( self.routers[point[1]][0] * weight )
      y_coord += ( self.routers[point[1]][1] * weight )
      self.store_centroid(point, x_coord, y_coord)
    return self.avg_centroid(point)

  def store_centroid(self, key, x, y):
    """
    Stores the old centroid values so that they can be averaged out.
    """
    if key not in centroid_store:
      centroid_store[key] = []
    centroid_store[key].append((x, y))
    if len(centroid_store[key]) > 5:
      centroid_store[key] = centroid_store[key][1:]

  def avg_centroid(self, key):
    """
    Returns the average centroid stored in the store.
    """
    data = self.centroid_store[key]
    denom = len(data)
    x = 0
    y = 0
    for point in data:
      x += point[0]
      y += point[1]
    return (x/denom, y/denom)

def main(sample_period,graphics=False):
    mgr = IOMgr()
    c = pipe.Collector(mgr,sample_period,"128.32.156.64","128.32.156.67","128.32.156.131","128.32.156.45")
    floor = Floor('floor4.png',c)
    floor.add_router('128.32.156.131',(116,147))
    floor.add_router('128.32.156.64' ,(233,157))
    floor.add_router('128.32.156.67' ,(589,117))
    floor.add_router('128.32.156.45' ,(466,132))
    if graphics:
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
        time.sleep(sample_period)
        mgr.poll(sample_period)
        #data = c.get_data()
        #data = c.get_data_normalize_to_min()
        #print c.get_data_for_mac('00:26:bb:00:2f:df',True)
        #print floor.compute_centroid(c.get_data_for_mac('00:26:bb:00:2f:df',True))
        data = c.get_data_normalize_to_min()
        print c.get_data_for_mac('f8:0c:f3:1d:16:49',True,datadict=data)
        print c.get_data_for_mac('f8:0c:f3:1c:ec:a2',True,datadict=data)
        print c.get_data_for_mac('04:46:65:f8:1a:1d',True,datadict=data)
        #log_centroid = floor.compute_centroid(c.get_data_for_mac('f8:0c:f3:1d:16:49',True))
        lin_centroid = floor.compute_centroid_exp(c.get_data_for_mac('f8:0c:f3:1d:16:49',True ,datadict=data))
        lin_centroid2 = floor.compute_centroid_exp(c.get_data_for_mac('f8:0c:f3:1c:ec:a2',True,datadict=data))
        lin_centroid3 = floor.compute_centroid_exp(c.get_data_for_mac('04:46:65:f8:1a:1d',True,datadict=data))
        if graphics:
            #screen.blit(fl,(0,0))
            pygame.draw.circle(screen, (0,0,255), map(lambda x: int(x), lin_centroid), 5)
            pygame.draw.circle(screen, (225,0,0), map(lambda x: int(x), lin_centroid2), 5)
            pygame.draw.circle(screen, (0,255,0), map(lambda x: int(x), lin_centroid3), 5)
            pygame.display.flip()
        c.clear_data()
      except KeyboardInterrupt:
        c.kill()
        sys.exit(0)

if __name__=="__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10, int(sys.argv[2] if len(sys.argv) > 2 else 0))
