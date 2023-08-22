from flask import Flask, jsonify
from mta_api.stationtimes import StationTimes
from mta_api.stations import Stations
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/get-station-time/<stop_id>")
def get_station_time_by_id(stop_id):
    stations = StationTimes().get_train_time_by_station()
    stop = stations[stop_id]
    nBound = stop['north_bound_trains']
    nBound.sort()
    sBound = stop['south_bound_trains']
    sBound.sort()

    return jsonify({
        'statusCode': 200,
        'data': stop
    })
@app.route("/api/get-station-details")
def get_station_details():
    stations = Stations().stations
    return jsonify(stations)

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)