import pandas as pd

class FerryTrips:
  def __init__(self, csv_path='metadata/ferry_data/google_transit/trips.txt'):
    self.csv_path = csv_path
    self.df_trips = self.make_df()
  
  def make_df(self):
    df = pd.read_csv(self.csv_path)
    df.columns = df.columns.str.replace(' ', '_')
    return df

  def get_trips(self):
    trips = {}
    for row in self.df_trips.itertuples():
      trips[row.trip_id] = {
          'trip_id': row.trip_id,
          'service_id': row.service_id,
          'trip_headsign': row.trip_headsign
      }
      #stations.append(station_data)
    return trips