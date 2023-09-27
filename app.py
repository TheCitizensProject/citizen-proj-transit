from flask import Flask, jsonify
from mta_api.stationtimes import StationTimes
from mta_api.ferrystationtimes import FerryStationTimes
from mta_api.stations import Stations
from mta_api.tramstationtimes import TramStationTimes
import json
from flask_cors import CORS
import os

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

@app.route("/api/get-station-time-unified/<stop_id>")
def get_station_time_by_id_unified(stop_id):
    stations = StationTimes().get_train_time_by_station()
    stop = stations[stop_id]
    nBound = stop['north_bound_trains']
    #sort
    nBound.sort(key=(lambda x: x[1]))
    nBound[0].append(stop['north_bound_label'])
    sBound = stop['south_bound_trains']
    #sort
    sBound.sort(key=(lambda x: x[1]))
    sBound[0].append(stop['south_bound_label'])
    #unify north and south bound trains
    if nBound[0][1] > sBound[0][1]:
        both_directions = [ [ sBound[0] ]+[ nBound[0] ] ]
    else:
        both_directions = [ [ nBound[0] ]+[ sBound[0] ] ]

    stop['both_directions'] = both_directions

    return jsonify({
        'statusCode': 200,
        'data': stop
    })

@app.route("/api/get-station-details")
def get_station_details():
    stations = Stations().stations
    return jsonify(stations)

@app.route("/api/get-ferry-time")
def get_ferry_times():

    stations = FerryStationTimes().get_ferry_time_by_station()
    stop = stations[25]
    #sort the times
    stop['ferry_times'].sort(key=(lambda x: x[-1]))

    removeUntil = -1 #init removeUntil
    #don't show negative departures
    for i in range(len(stop['ferry_times'])):
        if stop['ferry_times'][i][-1] < 0:
            removeUntil = i
    
    stop['ferry_times'] = stop['ferry_times'][removeUntil+1:]


    return jsonify({
        'statusCode': 200,
        'data': stop
    })

@app.route("/api/get-tram-time")
def get_tram_times():

    stations = TramStationTimes().get_tram_time_by_station()
    stop = stations[1]
    #sort the times
    stop['tram_times'].sort(key=(lambda x: x[1]))

    return jsonify({
        'statusCode': 200,
        'data': stop
    })

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)