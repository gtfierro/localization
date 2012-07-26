import server
import os
import sys
import json
from flask import Flask, render_template, url_for
import appstack
app = Flask(__name__, static_folder='static')
a = appstack.Appstack('local', '410soda', url='http://128.32.156.60:8000')

@app.route('/')
def main():
    return render_template('map.html')

@app.route('/off/<zone>')
def off(zone):
    a('.LIG < !Zone %s < !Floor 4 < !Sutardja Dai Hall' % zone)[0].set_level(1)
    return '1'

@app.route('/on/<zone>')
def on(zone):
    a('.LIG < !Zone %s < !Floor 4 < !Sutardja Dai Hall' % zone)[0].set_level(3)
    return '1'

if __name__ == '__main__':
  for l in a('.LIG < !Floor 4 < !Sutardja Dai Hall'):
    
    l.set_level(3)

  port = int(os.environ.get('PORT', 8001))
  app.run(debug=True, port=port)
