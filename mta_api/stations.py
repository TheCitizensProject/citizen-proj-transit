import pandas as pd

class Stations:
  """
  The Stations class is a higher order class that reads from a csv file with station
  metadata. This station metadata is usually provided by the transit authority, MTA, and
  can be found here: http://web.mta.info/developers/developer-data-terms.html#data.

  Download the Stations file, and save the csv under metadata dir, and point the path of the
  file in csv_path. 
  """
  def __init__(self, csv_path="./metadata/Stations.csv"):
    self.csv_path = csv_path
    self.df_stations = self.make_df()
    #self.stations = self.get_stations()

  def make_df(self):
    df = pd.read_csv(self.csv_path)
    df.columns = df.columns.str.replace(' ', '_')
    return df

  def get_stations(self):
    """
    This function is responsible for processing the Stations.csv file, and serving as a 
    data structure for storing stations data. We structure the data as follows:
            stations = {
                "station_gtfs_id_1" : {...}, "station_gtfs_id_2" : {...}, ...
            }
    We index with station_gtfs_id in order to make search operations faster later when we
    parse GTFS feed data, where we'll need to map the stop_id in gtfs form to this index.
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
          'south_bound_label': row.South_Direction_Label
      }
      #stations.append(station_data)
    return stations