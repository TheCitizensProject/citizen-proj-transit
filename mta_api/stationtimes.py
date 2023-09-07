from .feed_parser import FeedParser
from .stations import Stations
import time

class StationTimes:
  """
  StationTimes inherits from the Stations Class and inserts train times in the north and south
  bound platforms from parsed GTFS feed.
  """
  def __init__(self):
    super().__init__()
    self.feed = FeedParser().mta_feed
    self.df_stations = Stations().make_df()
    self.stations =  self.get_stations()

  #Set a time threshold in seconds for how far into future we'll display incoming trains.
  MINUTES_IN_FUTURE = 30
  TIME_THRESHOLD = 60*MINUTES_IN_FUTURE #Here 60 denotes 60 seconds in a minute

  def get_stations(self):
    """
    This method overrides the get_stations method from the Stations class, and adds two new
    fields- north_bound_trains and south_bound_trains. The two new field will track incoming
    trains on the respective platforms.
    """
    stations = {}
    for row in self.df_stations.itertuples():
      stations[row.GTFS_Stop_ID] = {
          'station_id': row.Station_ID,
          'station_name': row.Stop_Name,
          'gtfs_stop_id': row.GTFS_Stop_ID,
          'geo-loc': {
            'latitude': row.GTFS_Latitude,
            'longitude': row.GTFS_Longitude,
          },
          'north_bound_label': row.North_Direction_Label,
          'south_bound_label': row.South_Direction_Label,
          'north_bound_trains': [],
          'south_bound_trains': []
      }
      #stations.append(station_data)
    return stations

  def get_train_time_by_station(self):
    """
    This is the main method where we parse from the GTFS->JSON data, to display
    train times for every station.

    To find data on incoming trains from the GTFS feed, we need to look for the 
    stopTimeUpdate field nested within tripUpdates field. Below is the algorithm:

        1.for every entity in the feed:
          2.check if tripUpdates and stopTimeUpdates in tripUpdates exists:
            3.ifExist:
              4.check if they are valid stop times. A valid stop time is defined if the key
                arrival exists, and if the time of the next train is within threshold.
                5. ifValid:
                  6. for every update, do:
                    - The stop id in the feed is in the form 'RO6N', where 'R06' denotes
                      the gtfs stop id, and 'N' denotes whether its a north/south bound train.
                    - identify the gtfs stop id, the search term, and direction.
                    - Do a search on the stations dictionary with the search term. 
                    - Append the arrival time in respective north/south bound array.
                    - Note: The times being appended are not in a sorted order. We do not implement a sort
                      during this parsing to reduce the overhead. We can sort this data later on an API level.
    """
    for entity in self.feed:
      if 'tripUpdate' in entity.keys() and "stopTimeUpdate" in entity['tripUpdate'].keys():
        stop_time_updates = entity['tripUpdate']['stopTimeUpdate']

        valid_stop_times = [stop_time_update for stop_time_update in stop_time_updates
                            if self.is_valid_stop_time(stop_time_update)]

        for stop_time_update in valid_stop_times:
          search_term = stop_time_update['stopId'][:len(stop_time_update['stopId'])-1]
          direction = stop_time_update['stopId'][-1]
          if search_term in self.stations.keys():
              train = entity['tripUpdate']['trip']['routeId']
              posix_time = stop_time_update['arrival']['time']
              time_diff = self.get_time_difference(posix_time)
              #train_data = {'train':train,'time':round(time_diff/60)}
              train_data = (train, round(time_diff/60))
              if direction == 'N':
                self.stations[search_term]['north_bound_trains'].append(train_data)
              elif direction == 'S':
                self.stations[search_term]['south_bound_trains'].append(train_data)
    return self.stations

  def is_valid_stop_time(self, stop_time_update):
    arrival = stop_time_update.get('arrival')
    if arrival is None:
      return False
    time_diff = self.get_time_difference(arrival['time'])
    return 0 < time_diff < self.TIME_THRESHOLD



  @staticmethod
  def get_time_difference(str_posix_time):
    """Return time difference between current time and train arrival/departure time in seconds"""
    return float(str_posix_time) - time.time()

