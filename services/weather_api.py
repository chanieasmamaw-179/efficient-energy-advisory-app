"""
This module imports necessary libraries for making HTTP requests and handling type annotations
for data structures such as dictionaries and optional values.
"""
from typing import Dict, Optional
import requests

class WeatherService:
    """
    A service class to interact with a weather API using the provided API key.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_weather(self, city: str) -> Optional[Dict]:
        """
        Fetch weather data from the API and return the current temperature in Celsius.
        """
        try:
            url = (f"http://api.openweathermap.org/data/2.5/weather?q={city}"
                   f"&appid={self.api_key}&units=metric")  # units=metric for Celsius

            # Adding timeout to avoid hanging indefinitely
            response = requests.get(url, timeout=10)  # 10 seconds timeout

            if response.status_code == 200:
                data = response.json()
                return data

            print(f"Error: Unable to fetch weather data. Status code {response.status_code}")
            return None

        except requests.exceptions.RequestException as e:
            # This will catch any exception related to requests (network, timeout, etc.)
            print(f"Error fetching weather data: {str(e)}")
            return None
