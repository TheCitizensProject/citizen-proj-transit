import requests
import json
import os

class WeatherDetails:
    def __init__(self):
        self.weather_api_endpoint = "http://api.weatherapi.com/v1/current.json?key="
        self.headers = {
            "weather-api-key": os.getenv("WEATHER-KEY")
        }

    def get_weather_details(self):
        print("inside get weather details function")
        url=self.weather_api_endpoint + self.headers["weather-api-key"] + '&q=Roosevelt'
        print("URL:- ",url)
        response = requests.get(url)
        data=response.json()
        weather_data={
            "temp_f":data['current']['temp_f'],
            "condition":data['current']['condition']['text'],
            "icon":data['current']['condition']['icon']
        }
        return weather_data