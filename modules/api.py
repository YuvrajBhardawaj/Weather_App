import requests
from opencage.geocoder import OpenCageGeocode
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
from PIL import Image, ImageTk

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
    #print(response)
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
    """Fetches 5-day forecast from OpenWeatherMap API and extracts daily summaries."""
    API_KEY = "YOUR_API_KEY"
    api_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"

    response = requests.get(api_url).json()
    #print(response['list'])
    if response.get("cod") != "200":
        print("Error:", response.get("message"))
        return {}

    daily_forecast = {}
    
    for entry in response["list"]:
        date_obj = datetime.fromtimestamp(entry["dt"])
        date = date_obj.strftime('%Y-%m-%d')
        day = date_obj.strftime('%A')  # Get the day of the week
        temp = entry["main"]["temp"]
        condition = entry["weather"][0]["description"]
        icon = entry['weather'][0]['icon']

        if date not in daily_forecast:
            daily_forecast[date] = {"temp": temp, "condition": condition, "day": day, "icon" : icon}

    # Formatting forecast with day name
    forecast = [
        {"temp": data["temp"], "condition": data["condition"], "day": data["day"], "icon": data["icon"]}
        for date, data in daily_forecast.items()
    ]

    return forecast
def get_icon(icon_code):
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    try:
        response = requests.get(icon_url)
        return response
    except Exception as e:
        print("Error in loading icon : ",e)
    return None