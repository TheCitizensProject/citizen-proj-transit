from .ferrystations import FerryStations
from .feed_parser import FeedParser
from .ferrytrips import FerryTrips
import datetime
import time
import pandas as pd
import pytz

class FerryStationTimes:
  """
  This class will particularly deal with Roosevelt Island ferry. This is not
  as dynamic as the MTA Feed.
  """
  def __init__(self):
    self.feed = FeedParser().ferry_feed
    self.df_stations = FerryStations().make_df()
    self.stations =  self.get_stations()
    self.trips = FerryTrips().get_trips()
    

  TIME_THRESHOLD = 60*30 #1m*30 = 30m
  ROOSEVELTISLAND_STOP_ID = 25

  def get_stations(self):
    stations = {}
    for row in self.df_stations.itertuples():
      if row.stop_id == self.ROOSEVELTISLAND_STOP_ID:
        stations[row.stop_id] = {
            "gtfs_stop_id": row.stop_id,
            "station_name": row.stop_name,
            "geo-loc": {
              "latitude": row.stop_lat,
              "longitude": row.stop_lon,
            },
            "ferry_times": []
        }
      #stations.append(station_data)
    return stations
  
  def get_static_stop_times(self):
    """
    This method is responsible for parsing the static ferry feed provided by
    stop_times.txt. We only query for ROOSEVELTISLAND_STOP_ID station or whatever stop
    id is placed there.

    The trips object from the trips.txt file provides us service_id [1 or 2] which enables
    us to identify whether the line we are parsing is a weekend service or not. Depending
    on whether today is a weekend or weekday, we select the appropriate rows for display.
    
    Returns an array [(Ferry Bound, mins away),(...),...]
    """
    stop_times_df = pd.read_csv('metadata/ferry_data/google_transit/stop_times.txt')
    is_weakend = self.isWeekend()
    scheduled = []

    for row in stop_times_df.itertuples():
      if row.stop_id == self.ROOSEVELTISLAND_STOP_ID and self.trips[row.trip_id]['service_id']==is_weakend:
        #print(row)
        toPosix = self.toPOSIX(row.departure_time)
        if self.is_valid_stop_time(toPosix):
          dept_time = self.to_12Hours(row.departure_time)
          direction = self.trips[row.trip_id]['trip_headsign']
          scheduled.append((direction, dept_time))
    return scheduled

  def get_ferry_time_by_station(self):
    """
    This is the main method where we parse from the RT GTFS->JSON data, to display
    ferry times for every station. In particular, this method will return stop_times
    for station indicated within self.ROOSEVELTISLAND_STOP_ID, which is 25.

    There are two feeds we are getting data from, which sets parsing Ferry times as 
    different compared to Train times: 1) We are using the RT feed to get immediate
    ferries departing the station, 2) we are using the static feed to get the subsequent
    ferries that are scheduled within a TIME_THRESHOLD. We need to use the static feed
    because, unlike in Train feed, the RT feed for ferries do not show incoming ferries
    that are within a 30min-1hour window.

    This algorithm is quite similar to the StationTimes algorithm to parse data, such that
    we look for stopTimeUpdates in tripUpdate. However, since the data returned from RT is different
    from the Train RT feed, we need to adjust how we extract the direction. To extract the
    direction of where the ferry is headed, we leverage the trips.txt file from the static feed
    and map trip_id to the corresponding trip_haedsign. Each trip_id is associated with a particular
    direction represented as trip_headsign.
    """
    stop_times_rt = []
    for entity in self.feed:
      if 'tripUpdate' in entity.keys() and "stopTimeUpdate" in entity['tripUpdate'].keys():
        stop_time_updates = entity['tripUpdate']['stopTimeUpdate']
        for stopTimes in stop_time_updates:
          if 'departure' in stopTimes:
            if stopTimes['stopId']==str(self.ROOSEVELTISLAND_STOP_ID):
              gtfs_trip_id = entity['tripUpdate']['trip']['tripId']
              #map to direction from trips.txt
              direction = self.trips[int(gtfs_trip_id)]['trip_headsign']
              departure = stopTimes['departure']['time']
              departure_time_relative = self.get_time_difference(departure) // 60
              stop_times_rt.append((direction, str(departure_time_relative)))
    
    self.stations[self.ROOSEVELTISLAND_STOP_ID]['ferry_times'].extend(stop_times_rt)
    """
    So when real time feed is empty, we want to query the stop_times dataframe to get the next scheduled ferry.
    To do this, we use the stop_times.txt, and map:
    1. map stop_times.txt trip_id to trips.txt trip_id, and check whether service id is 1 or 2
      - 1=weekday, 2=weekend
    2. Based on service id, extract the time from stop_times.txt, and show 2 hours inbound.
    """
    scheduled = self.get_static_stop_times()
    self.stations[self.ROOSEVELTISLAND_STOP_ID]['ferry_times'].extend(scheduled)

    return self.stations


  @staticmethod
  def get_time_difference(str_posix_time):
    """Return time difference between current time and train arrival/departure time in seconds"""
    return float(str_posix_time) - time.time()
  
  @staticmethod
  def isWeekend():
    """
    Utility function to check whether today is a weekday or the weekend.
    Returns:
        2: if today is a weekend. 
        1: if today is not a weekend.
    Values 1 and 2 corresponds the static trips.txt file.
    """
    # Get the current date
    current_date = datetime.date.today()
    # Check if the day of the week is Saturday (5) or Sunday (6)
    if current_date.weekday() == 5 or current_date.weekday() == 6:
        return 2
    else: return 1
  
  @staticmethod
  def toPOSIX(input_time):
    """
    Utility function to convert the static 24hour time to UNIX time from stop_times.txt file.
    """
    # Your input time and date
    desired_timezone = "America/New_York"
    # Get the current date
    current_date = datetime.datetime.now().date()
    # Combine the current date and input time
    combined_datetime = datetime.datetime.combine(current_date, datetime.datetime.strptime(input_time, "%H:%M:%S").time())
    # Convert the combined datetime to the desired timezone
    timezone = pytz.timezone(desired_timezone)
    combined_datetime_timezone_aware = timezone.localize(combined_datetime)
    # Convert the timezone-aware datetime to Unix timestamp
    unix_timestamp = str(combined_datetime_timezone_aware.timestamp())
    return unix_timestamp

  def is_valid_stop_time(self, str_posix_time):
    time_diff = self.get_time_difference(str_posix_time)
    return 0 < time_diff < self.TIME_THRESHOLD

  @staticmethod
  def to_12Hours(input_time):
    """
    Utility function to convert static 24hour time to 12hour time from stop_times.txt file.
    """
    time_obj = datetime.datetime.strptime(input_time, '%H:%M:%S')
    formatted_time = time_obj.strftime('%I:%M:%S %p')
    return formatted_time