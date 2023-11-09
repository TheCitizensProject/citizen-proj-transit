from mta_api.ferrystationtimes import FerryStationTimes
from mta_api.feed_parser import FeedParser
from typing import Dict
import json
import pandas as pd

def test_get_ferry_stationtimes():
    feed = FeedParser().get_ferry_feed()
    stations = FerryStationTimes(feed=feed, testing=True).get_ferry_time_by_station()

    assert type(stations) == type(dict())


def test_ferry_cal():
    """
    Check to see if ferry calander.txt has 2 rows of entry. If more than 2 rows of entry is found, then inspect
    the entire ferry codebase or try to understand what has changed. Reference Issue #5 at https://github.com/TheCitizensProject/citizen-proj-transit/issues/5
    """
    df_cal = pd.read_csv("metadata/ferry_data/google_transit/calendar.txt")

    assert len(df_cal) == 2