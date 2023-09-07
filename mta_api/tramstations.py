from .stations import Stations

class TramStations(Stations):
  def __init__(self):
    super().__init__(csv_path="metadata/tram_data/google_transit/stops.txt")
    self.df_stations = self.make_df()

  def get_stations(self):

    stations = {}
    for row in self.df_stations.itertuples():
      if row.stop_id == 3:
        #all other stops belong to the buses
        break
      stations[row.stop_id] = {
          "gtfs_stop_id": row.stop_id,
          "station_name": row.stop_name,
          "geo-loc": {
            "latitude": row.stop_lat,
            "longitude": row.stop_lon,
          }
      }
    return stations