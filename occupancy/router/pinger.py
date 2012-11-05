import redis
import os
import subprocess

r = redis.Redis()

processes = {} # key: client-ip, value: ping process

try:
  while True:
      for ip in r.hgetall('ipmac'):
          if ip not in processes.keys():
              processes[ip] = subprocess.Popen('ping %s' % ip, shell=True)
except Exception as e:
  print e
  for ip in processes:
      processes[ip].kill()

    
