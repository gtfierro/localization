import which
import os
import sys
from flask import Flask, jsonify

app = Flask(__name__)

if len(sys.argv) > 2:
  chan = int(sys.argv[1])
else:
  chan = 11

l = Localizer(chan = chan, graphics = False)

@app.route('/<coord>/<index>')
def measure(coord,index):
  x,y = coord.split(',')
  l.run(duration=90,coord=(x,y),loc_index=index)
  return 'success!'

if __name__='__main__':
  port = int(os.environ.get('PORT',8080))
  app.run(host='0.0.0.0',port=port)
