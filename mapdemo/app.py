from flask import Flask, request, jsonify, Response, render_template
import json
import redis
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('base.html', user_ip = request.remote_addr)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/zone_data")
def zone_data():
    try:
        f = open('../occupancy/router/data.json', 'r')
        return Response(f.read(), mimetype='application/json')
    except:
        return jsonify(error=1)

def _get_default_pref():
  h = random.randint(0, 360)
  s = random.random()
  l = random.random()
  return {'h': h, 's': s, 'l': l}

@app.route("/client_data")
def client_data():
    r = redis.Redis()
    data = []
    loc_dict = r.hgetall('client_location')
    for (mac, loc_data) in loc_dict.items():
      pref_data = r.hget('client_pref', mac)
      if pref_data == None:
        pref = _get_default_pref()
        r.hset('client_pref', mac, json.dumps(pref))
      else:
        pref = json.loads(pref_data)

      client_data = json.loads(loc_data)
      client_data.update({'mac': mac})
      client_data.update(pref)
      data.append(client_data)

    return jsonify(data=data)

@app.route('/update_pref')
def update_pref():
    ip = request.remote_addr
    h = request.args.get('h')
    s = request.args.get('s')
    l = request.args.get('l')

    data = json.dumps({'h': h, 's': s, 'l': l})
    r = redis.Redis()
    mac = r.hget('ipmac', ip)
    if mac == None:
      return jsonify(error="Unknown IP")

    r.hset('client_pref', mac, data)
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
