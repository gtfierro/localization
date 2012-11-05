import redis
import time
import json
import random

r = redis.Redis()

while True:
  for (mac, ip) in zip(['0a:f6:b1:19:aa:bb', '0a:f6:b1:19:00:11', '0a:f6:b1:19:cc:dd'],
                     ['127.0.0.1', '10.10.123.123', '10.10.123.124']):
    r.hset('macip', mac, ip)
    r.hset('ipmac', ip, mac)

    data = json.dumps({'x': random.randint(0,599), 'y': random.randint(0, 240), 'ip': ip})
    print mac, data
    r.hset('client_location', mac, data)
  time.sleep(3)
