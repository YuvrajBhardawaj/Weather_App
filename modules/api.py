import requests
from opencage.geocoder import OpenCageGeocode
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz

GEOCODER_KEY = "6196d0b477804722ae736e5369a090df"
WEATHER_API_KEY = "a6e10cd2405910e88e1a9ea700f6995c"

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
    """Fetches weather data from OpenWeatherMap API."""
    location = get_location(city)
    if not location:
        return None

    lat, lng = location["lat"], location["lng"]
    api_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(api_url).json()
    print(response)
    if response.get("cod") == 200:  # Check if request was successful
        return {
            "pressure": response['main']['pressure'],
            "humidity": response['main']['humidity'],
            "wind_speed": response['wind']['speed'],
            "description": response['weather'][0]['description'],
            "temperature": response['main']['temp'],
            "feelslike": response['main']['feels_like'],
            "icon":response['weather'][0]['icon']
        }
    return None

def get_weekly_forecast(city):
    """Fetches 7-day forecast from OpenWeatherMap API."""
    location = get_location(city)
    print(location)
    if not location:
        return None

    lat, lng = 11.4,77.3
    api_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&exclude=current,minutely,hourly,alerts&units=metric&appid={WEATHER_API_KEY}"

    response = requests.get(api_url).json()
    print(response)
    if "daily" in response:
        forecast = []
        for day in response["daily"]:
            date = datetime.fromtimestamp(day["dt"]).strftime('%A, %d %b %Y')
            temp = day["temp"]["day"]
            condition = day["weather"][0]["description"]
            forecast.append(f"{date}: {temp}°C, {condition}")
        return forecast
    return None