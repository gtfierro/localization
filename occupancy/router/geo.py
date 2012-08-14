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


  def compute_centroid(self, data):
    """
    Computes the (x,y) position of the centroid given [data].
    [data] is a list of tuples (RSSI, router-ip), where RSSI is a negative number in dBM
    and router-ip is a string corresponding to one of the routers we've registered with
    this Floor
    """
    sum_reciprocal = sum(map(lambda x: 1.0 / abs(float(x[0])), data))
    x_coord = 0
    y_coord = 0
    for point in data:
      if point[1] not in self.routers.keys():
        continue
      x_coord += ( self.routers[point[1]][0] / abs(float(point[0])) )
      y_coord += ( self.routers[point[1]][1] / abs(float(point[0])) )
    x_coord /= sum_reciprocal
    y_coord /= sum_reciprocal
    print x_coord, y_coord
    return (x_coord, y_coord)


def main(sample_period):
    mgr = IOMgr()
    c = pipe.Collector(mgr,sample_period,"128.32.156.64","128.32.156.67","128.32.156.131","128.32.156.45")
    floor = Floor('floor4.png',c)
    floor.add_router('128.32.156.131',(116,147))
    floor.add_router('128.32.156.64' ,(233,157))
    floor.add_router('128.32.156.67' ,(589,117))
    floor.add_router('128.32.156.45' ,(466,132))
    while True:
      try:
        time.sleep(sample_period)
        mgr.poll(sample_period)
        data = c.get_data()
        print c.get_data_for_mac('00:26:bb:00:2f:df',True)
        print floor.compute_centroid(c.get_data_for_mac('00:26:bb:00:2f:df',True))
        c.clear_data()
      except KeyboardInterrupt:
        c.kill()
        sys.exit(0)

if __name__=="__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10)
