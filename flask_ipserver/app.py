import os
from flask import Flask, jsonify, request
app = Flask(__name__)

routers = {}


@app.route('/')
def index():
  return jsonify(routers)

@app.route('/reg/<name>')
def register(name):
  routers[request.remote_addr] = name
  return jsonify(routers)

if __name__=="__main__":
  port = int(os.environ.get('PORT',8080))
  app.run(host='0.0.0.0',port=port,debug=True)
