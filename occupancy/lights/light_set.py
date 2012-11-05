import redis
import json
import sys
import time
import requests
from numpy import mean

timeout = 0.5

r = redis.Redis()  
building = json.loads(open('../router/data.json').read())
zones = building['zones']
light_zones = building['light_zones']

def _set_color(light, h, s, b):
  ''' light: dict of {'server': Hue bridge, 'lamp': Lamp number}
      h: hue 0-360
      s: saturation 0-1
      b: brigtness 0-1
  '''
  h = (h/360.0) * 65535.0
  s = s * 254.0
  b = b * 254.0

  print "Setting light", light, "to", h,s,b
  if b == 0:
    writes = [json.dumps({'bri': 0, 'on': True})]
  else:
    writes = [json.dumps({'bri': b, 'on': True}), json.dumps({'hue': h, 'sat': s})]

  for data in writes:
    try:
      r = requests.put("http://%s/api/YourAppName/lights/%d/state" % (light['server'], light['lamp']), data, timeout=timeout)
      res = json.loads(r.text)
      for r in res:
        if 'error' in r.keys():
          print "Error writing:", data
          print res
          if r['error']['type'] == 901:
            time.sleep(0.1)
            print "Continuing"
          else:
            sys.exit(1)
    except requests.exceptions.Timeout:
      print "Timeout"
    except requests.exceptions.ConnectionError:
      print "Connection Error"

def get_zone(loc):
  global zones
  for (z_idx, z) in enumerate(zones):
    (xul, yul) = z[0]
    (xlr, ylr) = z[2]
    if loc['x'] >= xul and loc['x'] <= xlr \
      and loc['y'] >= yul and loc['y'] <= ylr:
      return z_idx
  return None

while True:
  # Clients per zone
  zone_clients = []
  for z in zones:
    zone_clients.append([])

  # Collect client color preferences
  loc_dict = r.hgetall('client_location')
  for (mac, loc_data) in loc_dict.items():
    pref_data = r.hget('client_pref', mac)
    if pref_data != None:
      pref = json.loads(pref_data)
      zone = get_zone(json.loads(loc_data))
      zone_clients[zone].append(pref)

  # Find average color
  for (clients, light) in zip(zone_clients, light_zones):
    if light != None:
      if len(clients) == 0:
        _set_color(light, 0, 0, 0)
      else:
        h = mean([float(c['h']) for c in clients])
        s = mean([float(c['s']) for c in clients])
        l = mean([float(c['l']) for c in clients])
        _set_color(light, h, s, l)

  time.sleep(5)
