from flask import Flask, request, jsonify, Response, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('base.html')

@app.route("/data")
def getdata():
    try:
        f = open('../occupancy/router/data.json', 'r')
        return Response(f.read(), mimetype='application/json')
    except:
        return jsonify(error=1)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
