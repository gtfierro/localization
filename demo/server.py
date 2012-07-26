import server
import os
import json
from flask import Flask, render_template, url_for
import appstack
app = Flask(__name__, static_folder='static')
a = appstack.Appstack('local', '410soda', url='http://128.32.156.60:8000')

@app.route('/')
def main():
    return render_template('map.html')

@app.route('/isolate/<zone>')
def actuate(zone):
    for n in range(2, 6):
        if int(zone) != n:
            a('.LIG < !Zone %s < !Floor 4 < !Sutardja Dai Hall' % n)[0].set_level(0)
    a('.LIG < !Zone %s < !Floor 4 < !Sutardja Dai Hall' % zone)[0].set_level(3)
    return 'Yay!'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(debug=True, port=port)
