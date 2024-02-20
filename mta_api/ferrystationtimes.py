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

  Update Sept 25th:
  - To fix implementation of ferry
  """
  def __init__(self, feed:str):
    self.feed = feed
    self.df_stations = FerryStations().make_df()
    self.stations =  self.get_stations()
    self.trips = FerryTrips().get_trips()
    self.stop_times_df = pd.read_csv('metadata/ferry_data/google_transit/stop_times.txt')
    self.static_times = self.get_static_timetable()
    

  TIME_THRESHOLD = 60*60 #1m*30 = 30m
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
  
  def get_static_timetable(self):
    """
    """
    stop_times_df = self.stop_times_df
    static_times = {}
    for row in stop_times_df.itertuples():
      key = (row.trip_id, row.stop_id)
      static_times[key] = {
          'arrival_time': self.toPOSIX(row.arrival_time),
          'departure_time': self.toPOSIX(row.departure_time)
      }
    
    return static_times
  
  def get_schedule(self):
    """
    This method is responsible for parsing the static ferry feed provided by
    stop_times.txt. We only query for ROOSEVELTISLAND_STOP_ID station or whatever stop
    id is placed there.

    The trips object from the trips.txt file provides us service_id [1 or 2] which enables
    us to identify whether the line we are parsing is a weekend service or not. Depending
    on whether today is a weekend or weekday, we select the appropriate rows for display.
    
    Returns an array [(Ferry Bound, mins away),(...),...]
    """
    stop_times_df = self.stop_times_df
    is_weakend = self.isWeekend()
    #print(is_weakend)
    scheduled = []

    for row in stop_times_df.itertuples():
      if row.stop_id == self.ROOSEVELTISLAND_STOP_ID and self.trips[row.trip_id]['service_id'] == is_weakend:
        #print(row)
        toPosix = self.toPOSIX(row.departure_time)
        if self.is_valid_stop_time(toPosix):
          #change from 12hr time to time difference
          #dept_time = self.to_12Hours(row.departure_time)
          dept_time = round(self.get_time_difference(toPosix)/60)
          direction = self.trips[row.trip_id]['trip_headsign']
          scheduled.append([row.trip_id,direction,row.departure_time, dept_time])
    return scheduled

  def get_ferry_time_by_station(self):
    """
    This is the main method where we parse from the RT GTFS->JSON data, to display
    ferry times for every station. In particular, this method will return stop_times
    for station indicated within self.ROOSEVELTISLAND_STOP_ID, which is 25.
    """
    scheduled = self.get_schedule()
    #make a hashset for efficient search
    rt_feed = {}
    for entity in self.feed:
      rt_feed[entity['id']] = entity
    # print(rt_feed)
    #get differences
    scheduled_filtered = []
    for schedule in scheduled:
      trip_id = str(schedule[0])
      if trip_id not in rt_feed.keys():
        print("Schedule not there", schedule)
        continue
      entity = rt_feed[trip_id]
      if 'tripUpdate' in entity.keys():
        """
        Instead of looping through every stop time update, just take the last the
        last index for comparison. There are 2 cases:
        1. The last index is that of the target station, aka Roosevelt Island.
        2. The last index is that of a preceeding station

        For both the cases, we need to check:
        1. whether departure information is there
        2. if departure info exist:
          1. calculate the differences
        3. if departure info not exist:
          1. calculate differences based on arrival information.
        """
        stop_time_update = entity['tripUpdate']['stopTimeUpdate'][-1]
        key = (int(trip_id), int(stop_time_update['stopId']))
        static_time = self.static_times[key]
        delay = 0
        if 'departure' in stop_time_update.keys():
          rt_time = round(self.get_time_difference(stop_time_update['departure']['time'])/60)
          sch_time = round(self.get_time_difference(static_time['departure_time'])/60)
          if sch_time<rt_time:
            delay = abs(abs(rt_time)-abs(sch_time))
          stop_time_update['departure']['rt_time'] = rt_time
          stop_time_update['departure']['sch_time'] = sch_time
        else:
          rt_time = round(self.get_time_difference(stop_time_update['arrival']['time'])/60)
          sch_time = round(self.get_time_difference(static_time['arrival_time'])/60)
          if sch_time<rt_time:
            delay = abs(abs(rt_time)-abs(sch_time))
          stop_time_update['arrival']['rt_time'] = rt_time
          stop_time_update['arrival']['sch_time'] = sch_time

        #fix the schedule if delay exists
        schedule[-1] += delay
        scheduled_filtered.append(schedule)
    
    self.stations[self.ROOSEVELTISLAND_STOP_ID]['ferry_times'].extend(scheduled_filtered)

    return self.stations


  def parse_stops(self, stop):
    #sort the times
    stop['ferry_times'].sort(key=(lambda x: x[-1]))

    removeUntil = -1 #init removeUntil
    #don't show negative departures
    for i in range(len(stop['ferry_times'])):
        if stop['ferry_times'][i][-1] < 0:
            removeUntil = i
    
    stop['ferry_times'] = stop['ferry_times'][removeUntil+1:]
    #display only 2 ferries
    toShow = 2
    stop['ferry_times'] = stop['ferry_times'][:toShow]

  def get_static_schedule(self, stop):
    scheduled = self.get_schedule()
    unique_destinations = {}

    for route in scheduled:
      if route[-1] < 0:  # skip if the last element is negative
        continue

      destination = route[1]
      if destination not in unique_destinations and self.is_active(self, destination):
        unique_destinations[destination] = route

      # Exit the loop early when we have found two unique routes
      if len(unique_destinations) == 2:
        break

    stop['ferry_times_static'] = list(unique_destinations.values())
    
    
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

    ---Manual Fix Oct 2---
    hard code weekend and weekday but keep previous logic
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
    current_date = datetime.datetime.now(pytz.timezone(desired_timezone)).date()

    # Combine the current date and input time
    combined_datetime = datetime.datetime.combine(current_date, datetime.datetime.strptime(input_time, "%H:%M:%S").time())

    # Convert the timezone-aware datetime to Unix timestamp
    unix_timestamp = str(combined_datetime.timestamp())
    return unix_timestamp

  def is_valid_stop_time(self, str_posix_time):
    time_diff = self.get_time_difference(str_posix_time)
    #-15*60=-900: Go lookup schedule 15min behind to account for delays.
    #assume that a ferry could be delayed by a max of 15mins.
    return -900 < time_diff < self.TIME_THRESHOLD

  @staticmethod
  def to_12Hours(input_time):
    """
    Utility function to convert static 24hour time to 12hour time from stop_times.txt file.
    """
    time_obj = datetime.datetime.strptime(input_time, '%H:%M:%S')
    formatted_time = time_obj.strftime('%I:%M:%S %p')
    return formatted_time

  @staticmethod
  def is_active(self, destination):
    """
    Check if a ferry to a given destination is currently active based on the current time and 
    weekday, using a dictionary to store the ferry schedule times for each destination. Returns 
    False if the destination is not in the schedule.

    Using the most recent Winter schedule
    https://images.ferry.nyc/wp-content/uploads/2018/03/04020153/2023_winter_astoria.pdf
    to populate ferry_static_ref dictionary. 
    
    NOTE: This will need to be updated in the future, when the ferry schedule changes, or 
    when we update the zipped schedule with an updated schedule. 
    (https://www.ferry.nyc/developer-tools/)
    """
    ferry_static_schedule = {
      'East 90th St': {
        'weekday': ['07:02:00', '20:58:00'],
        'weekend': ['09:40:00', '20:07:00'],
      },
      'Wall St./Pier 11': {
        'weekday': ['06:17:00', '20:32:00'],
        'weekend': ['09:14:00', '19:41:00'],
      },
    }

    # Get the current local time
    current_time = datetime.datetime.now().time()
    is_weekend = self.isWeekend() == 2
    # Check if the destination is active
    if destination in ferry_static_schedule:
        schedule = ferry_static_schedule[destination]['weekend'] if is_weekend else ferry_static_schedule[destination]['weekday']
        start_time = datetime.datetime.strptime(schedule[0], "%H:%M:%S").time()
        end_time = datetime.datetime.strptime(schedule[1], "%H:%M:%S").time()
        return start_time <= current_time <= end_time
    else:
        return False