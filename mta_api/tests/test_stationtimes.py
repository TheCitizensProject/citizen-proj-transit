from mta_api.stationtimes import StationTimes
import json

# Opening JSON file
with open('sample_mta_rt_gtfs.json', 'r') as f: 
    # Reading from json file
    feed = json.load(f)

def test_get_station_time_by_id_unified():
    stop_id = "B06"
    stations = StationTimes(feed=feed, testing=True).get_train_time_by_station()
    stop = stations[stop_id]
    expected_output = {'station_id': 222, 'station_name': 'Roosevelt Island', 'gtfs_stop_id': 'B06', 'geo-loc': {'latitude': 40.759145, 'longitude': -73.95326}, 'north_bound_label': 'Queens', 'south_bound_label': 'Manhattan', 'north_bound_trains': [['F', 21], ['F', 41], ['F', 61]], 'south_bound_trains': [['F', 9], ['F', 29], ['F', 49]]}

    assert stop == expected_output