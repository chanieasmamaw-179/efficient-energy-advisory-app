import requests
from typing import Dict, Optional

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_weather(self, city: str) -> Optional[Dict]:
        """
        Fetch weather data from the API and return the current temperature in Celsius.
        """
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"  # units=metric for Celsius
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Error: Unable to fetch weather data. Status code {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            return None
