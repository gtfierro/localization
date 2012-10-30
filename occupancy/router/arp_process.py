import sys
import re
import time
import redis
import os

def is_reserved_ip(ip):
  # 10.10.0.* is reserved
  return ip.startswith('10.10.0.')

r = redis.Redis()
r.delete('macs')
r.delete('ipmac')

while True:
  os.system('scp root@10.10.0.1:/tmp/dhcp.leases /tmp/dhcp')

  with open('/tmp/dhcp') as f:
    for l in f.readlines():
      parts = l.split()
      if len(parts) > 3:
        (ts, mac, ip) = parts[0:3]
        if not is_reserved_ip(ip):
          print ip, mac
          r.sadd('macs', mac)
          r.hset('ipmac', ip, mac)
          r.hset('macip', mac, ip)

  print r.smembers('macs')
  print r.hgetall('ipmac')

  time.sleep(1)
