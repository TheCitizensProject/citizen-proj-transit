from flask import Flask
from mta_api.stationtimes import StationTimes
from mta_api.stations import Stations
import json

app = Flask(__name__)

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

    return stop
@app.route("/api/get-station-details")
def get_station_details():
    stations = Stations().stations
    return stations

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)