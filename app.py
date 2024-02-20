from mta_api.stationtimes import StationTimes
from mta_api.ferrystationtimes import FerryStationTimes
from mta_api.stations import Stations
from mta_api.tramstationtimes import TramStationTimes
from mta_api.feed_parser import FeedParser
import json
import os
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import api_docs.documentation as doc
from weather_api.weather_details import WeatherDetails

app = FastAPI(
    title=doc.title(),
    description = doc.description(),
    version="2.0.0",
    contact = doc.contact()
)

origins = ["*",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get("/api/get-station-time/{stop_id}")
def get_station_time_by_id(stop_id:str):
    feed = FeedParser().get_mta_feed()
    stations = StationTimes(feed=feed).get_train_time_by_station()
    stop = stations[stop_id]
    nBound = stop['north_bound_trains']
    nBound.sort()
    sBound = stop['south_bound_trains']
    sBound.sort()

    return {
        'statusCode': 200,
        'data': stop
    }

@app.get("/api/get-station-time-unified/{stop_id}")
def get_station_time_by_id_unified(stop_id: str):
    feed = FeedParser().get_mta_feed()
    stations = StationTimes(feed=feed).get_train_time_by_station()
    toShow = 1 #number of trains to show per direction
    stop = stations[stop_id]
    nBound = stop['north_bound_trains']
    #sort north bound
    nBound.sort(key=(lambda x: x[1]))
    #nBound[0].append(stop['north_bound_label'])
    for i in range(toShow):
        if i < len(nBound):
            nBound[i].append(stop['north_bound_label'])
    sBound = stop['south_bound_trains']
    #sort south bound
    sBound.sort(key=(lambda x: x[1]))
    #sBound[0].append(stop['south_bound_label'])
    for i in range(toShow):
        if i<len(sBound):
            sBound[i].append(stop['south_bound_label'])
    #unify north and south bound trains
    both_directions = nBound[:toShow]+sBound[:toShow]
    #sort both directions
    both_directions.sort(key=(lambda x: x[1]))

    stop['both_directions'] = both_directions

    return {
        'statusCode': 200,
        'data': stop
    }

@app.get("/api/get-station-details")
def get_station_details():
    stations = Stations().stations
    #return jsonify(stations)

@app.get("/api/get-ferry-time")
def get_ferry_times():
    feed = FeedParser().get_ferry_feed()
    ferry_station_times = FerryStationTimes(feed=feed)
    stations = ferry_station_times.get_ferry_time_by_station()
    stop = stations[25]

    if 'ferry_times' in stop.keys() and len(stop['ferry_times']) > 0:
        ferry_station_times.parse_stops(stop)
    else:
        ferry_station_times.get_static_schedule(stop)

    return {
        'statusCode': 200,
        'data': stop
    }

@app.get("/api/get-tram-time")
def get_tram_times():

    stations = TramStationTimes().get_tram_time_by_station()
    stop = stations[1]
    #sort the times
    stop['tram_times'].sort(key=(lambda x: x[1]))
    #display only two trams
    toShow = 2
    stop['tram_times'] = stop['tram_times'][:toShow]

    return {
        'statusCode': 200,
        'data': stop
    }

@app.get("/api/get-weather-data")
def get_weather_data():
    wd=WeatherDetails()
    data=wd.get_weather_details()
    print("data in app.py  ")
    return {
        'data': data
    }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)