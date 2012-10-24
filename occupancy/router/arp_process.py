import sys
import re
import redis
import os

os.system('scp root@10.10.0.1:/tmp/dhcp.leases /tmp/dhcp')

r = redis.Redis()
with open('/tmp/arp') as f:
  for l in f.readlines():
    parts = re.split('\s{3,}', l.strip())
    if len(parts) != 6:
      print "Error parsing:", l, parts
    else:
      (ip, hw_type, flags, mac, mask, dev) = parts
      if dev == 'br-lan':
        print ip, mac
        r.sadd('macs', mac)
        r.hset('ipmac', ip, mac)

print r.smembers('macs')
print r.hgetall('ipmac')

