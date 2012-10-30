import redis
import os

r = redis.Redis()

while True:
    for ip in r.hgetall('ipmac'):
        os.system('ping -c 1 %s' % ip)
    
