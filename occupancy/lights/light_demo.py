import sys
import requests
import json
import random
import time

max_step = 0.2
sleep_time = 0.2

def _set_color(h, s, b):
  bri_data = json.dumps({'bri': 30, 'on': True})
  color_data = json.dumps({'hue': h, 'sat': s})

  for lamp in [int(sys.argv[1]),]:
    for data in [bri_data, color_data]:
      try:
        r = requests.put("http://192.168.2.2/api/YourAppName/lights/%d/state" % lamp, data, timeout=0.5)
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


current_h = 1
current_s = 1
current_b = 1
def fade_to(h = None, s = None, b = None):
  global current_h, current_s, current_b, max_step
  if h == None: 
    h = current_h
  if s == None:
    s = current_s
  if b == None:
    b = current_b

  # compute steps rounding down
  h_steps = abs(h - current_h) / max_step
  s_steps = abs(s - current_s) / max_step
  b_steps = abs(b - current_b) / max_step
  steps = int(max(h_steps, s_steps, b_steps))

  if steps > 0:
    h_step = (h - current_h) / float(steps)
    s_step = (s - current_s) / float(steps)
    b_step = (b - current_b) / float(steps)
    for i in range(0, steps):
      current_h += h_step
      current_s += s_step
      current_b += b_step
      _set_color(int(current_h * 65535.0), int(current_s * 254), int(current_b * 252)+1) 
      print current_h, current_s, current_b
      time.sleep(sleep_time)
  current_h = h
  current_s = s
  current_b = b
  _set_color(int(current_h * 65535.0), int(current_s * 254), int(current_b * 252)+1)
  print current_h, current_s, current_b

while True:
  h = random.random()
  s = random.random()
  b = random.random()
  print "Fade", h, s, b
  fade_to(h, s, b)
