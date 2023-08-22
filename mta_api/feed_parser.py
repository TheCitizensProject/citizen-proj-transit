import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import time
from dotenv import load_dotenv
import os

load_dotenv()

class FeedParser:
  """
  The GTFS Feed Parsing Class. The objective is to get the relevant GTFS endpoints,
  and parse them into JSON.

  MTA Documentation: https://new.mta.info/developers

  In order to get the feed details and read up on the Real Time GFTS MTA Feed, refer
  to the document above, and make sure to obtain an API Key by registering with the MTA.
  """
  def __init__(self):
    self.mta_endpoints = {
      'BDFM': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm',
    }
    self.ferry_endpoint = "http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate"
    self.headers = {
      "x-api-key": os.getenv("MTA-KEY")
    }
    self.mta_feed = self.get_mta_feed()
    self.ferry_feed = self.get_ferry_feed()


  def get_mta_feed(self):
    feeds = []
    for endpoint in self.mta_endpoints:
      url = self.mta_endpoints[endpoint]
      feed = gtfs_realtime_pb2.FeedMessage()
      response = requests.get(url, headers=self.headers)
      feed.ParseFromString(response.content)
      feeds.extend(MessageToDict(feed)['entity'])
    #feeds_ = [j for sub in feeds for j in sub]
    return feeds
  
  def get_ferry_feed(self):
    url = self.ferry_endpoint
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(url)
    feed.ParseFromString(response.content)
    feed = MessageToDict(feed)['entity']

    return feed



"""
Feed references: 
  {
      'ACE': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace',
      'BDFM': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm',
      'G': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g',
      'JZ': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz',
      'NQRW': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw',
      'L': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
      '1234567': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
      'SIR': 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si'
  }
"""