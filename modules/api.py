import requests
from opencage.geocoder import OpenCageGeocode
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

GEOCODER_KEY = "6196d0b477804722ae736e5369a090df"
WEATHER_API_KEY = "ceb519c5f63b13eaa9abafae53bdc118"

def get_location(city):
    """Fetches latitude, longitude, and timezone of a city."""
    geocoder = OpenCageGeocode(GEOCODER_KEY)
    result = geocoder.geocode(city)

    if not result:
        return None

    lat, lng = result[0]['geometry']['lat'], result[0]['geometry']['lng']
    timezone_finder = TimezoneFinder()
    timezone = timezone_finder.timezone_at(lng=lng, lat=lat)

    if not timezone:
        return None

    local_time = datetime.now(pytz.timezone(timezone)).strftime("%I:%M %p")
    return {"lat": lat, "lng": lng, "timezone": timezone, "time": local_time}

def get_weather(city):
    """Fetches weather data from WeatherStack API."""
    api_url = f"http://api.weatherstack.com/current?access_key={WEATHER_API_KEY}&query={city}"
    response = requests.get(api_url).json()

    if "current" in response:
        print(response['current'])
        return {
            "pressure": response['current']['pressure'],
            "humidity": response['current']['humidity'],
            "wind_speed": response['current']['wind_speed'],
            "description": response['current']['weather_descriptions'][0],
            "temperature": response['current']['temperature'],
            "feelslike" : response['current']['feelslike'],
        }
    return None