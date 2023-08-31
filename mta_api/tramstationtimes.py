import datetime
import time
from tramstations import TramStations
import pytz
import pandas as pd

class TramStationTimes(TramStations):
  """
  This class will particularly deal with Roosevelt Island tram system. This is not
  as dynamic as the MTA Feed.
  """
  def __init__(self):
    super().__init__()
    self.stations =  self.get_stations()


  TIME_THRESHOLD = 60*60 #1m*30 = 30m
  ROOSEVELTISLAND_STOP_ID = 1

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
            "tram_times": []
        }
    return stations

  def get_static_stop_times(self):
    """
    Should return an array [(Tram Bound, mins away),(...),...]
    """
    stop_times_df = pd.read_csv('metadata/tram_data/google_transit/stop_times.txt')
    #drop duplicate entries:
    stop_times_df.dropna(subset=['stop_headsign'], axis=0, inplace=True)

    current_date = datetime.date.today()
    
    scheduled = []

    for row in stop_times_df.itertuples():
      if row.stop_id == self.ROOSEVELTISLAND_STOP_ID:
        
        toPosix = self.toPOSIX(row.departure_time)
        if toPosix == -1:
          #if dept time was more than 24hrs, we use -1 to ignore.
          continue
        
        if self.is_valid_stop_time(toPosix):
          
          if "car1_Standard" in row.trip_id:
            dept_time = self.to_12Hours(row.departure_time)
            direction = row.stop_headsign
            scheduled.append((direction, dept_time))
          if "car2_Mon-Fri_Rush" in row.trip_id and (current_date.weekday != 5 or current_date.weekday != 6):
            dept_time = self.to_12Hours(row.departure_time)
            direction = row.stop_headsign
            scheduled.append((direction, dept_time))
          if "car1_Fri-Sat_Extension" in row.trip_id and (current_date.weekday == 4 or current_date.weekday == 5):
            #print("car1_Fri-Sat_Extension")
            dept_time = self.to_12Hours(row.departure_time)
            direction = row.stop_headsign
            scheduled.append((direction, dept_time))
          elif ("Northbound_Standard" in row.trip_id or "Northbound_Weekend_Extension" in row.trip_id
                or "Northbound_Rush" in row.trip_id):
            break

    return scheduled

  def get_tram_time_by_station(self):
    """
    for every entity, check for tripUpdates and stopTimeUpdates
    """
    scheduled = self.get_static_stop_times()
    self.stations[self.ROOSEVELTISLAND_STOP_ID]['tram_times'].extend(scheduled)

    return self.stations


  @staticmethod
  def get_time_difference(str_posix_time):
    """Return time difference between current time and train arrival/departure time in seconds"""
    return float(str_posix_time) - time.time()


  @staticmethod
  def toPOSIX(input_time):
    # Your input time and date
    desired_timezone = "America/New_York"
    # Get the current date
    current_date = datetime.datetime.now().date()
    # Combine the current date and input time
    try:
      #there are instances of times that are more than 24hours, we ignore them.
      combined_datetime = datetime.datetime.combine(current_date, datetime.datetime.strptime(input_time, "%H:%M:%S").time())
    except:
      combined_datetime = -1
      return combined_datetime
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
    time_obj = datetime.datetime.strptime(input_time, '%H:%M:%S')
    formatted_time = time_obj.strftime('%I:%M:%S %p')
    return formatted_time
