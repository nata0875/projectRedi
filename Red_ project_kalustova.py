import asyncio
import datetime
import telegram
import googlemaps
import requests
import json


# Reading Api key from configuration file
with open('config.json') as config_file:
    config = json.load(config_file)
    GMAPS_API_KEY = config['API_KEY']
    BOT_TOKEN = config['BOT_TOKEN']
    chat_id = config['chat_id']  # chat identifier
    OPENWEATHERMAP_API_KEY = config['OPENWEATHERMAP_API_KEY']


# Making a function to send a message to Telegram
async def send_telegram_message(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=chat_id, text=message)


# Asking Google map API for route and duration
def get_route_and_duration(origin, destination):
    gmaps = googlemaps.Client(key=GMAPS_API_KEY)
    now = datetime.datetime.now()
    directions_result = gmaps.directions(origin, destination, departure_time=now, language='en-GB')

    if len(directions_result) > 0:
        route = directions_result[0]['summary']
        duration = directions_result[0]['legs'][0]['duration_in_traffic']['text']
        return f"Hi! Travel time is about: {duration}\nRoute: {route}\nDeparture:{origin}\nDestination:{destination}"
    else:
        return "There is not any reply"


# Asking API OpenWeatherMap current weather
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Kyiv&appid={OPENWEATHERMAP_API_KEY}&units=metric"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"Current weather: {description}, Temperature: {temperature}°C\n"
    else:
        return "Could not get weather information"


# Asking API OpenWeatherMap weather forecast
def get_weather_forecast():
    url = f"http://api.openweathermap.org/data/2.5/forecast?q=Kyiv&appid={OPENWEATHERMAP_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        forecast = data['list'][0:4]  # forecast for next 12 hours(every 3 hours)
        warning = "Goog luck!"
        for item in forecast:
            weather = item['weather'][0]['main']
            if weather == 'Rain':
                warning = "Expecting rain. Watch out and good luck!"
                break
            elif weather == 'Freezing rain':
                warning = "Expecting freezing rain. Watch out and good luck!"
                break
        return warning
    else:
        return "Could not get weather information"


# Creating message
async def send_route_message(origin, destination, time_hour):
    now = datetime.datetime.now()
    target_time = now.replace(hour=time_hour, minute=0, second=0, microsecond=0)

    while now < target_time:
        await asyncio.sleep(60)  # time check every minute роверка времени каждую минуту
        now = datetime.datetime.now()

    message = get_route_and_duration(origin, destination)
    weather = get_weather()
    forecast = get_weather_forecast()
    message += f"\n\n{weather}\n{forecast}"

    await send_telegram_message(message)


# Setting origin, destination,calling function send_route_message
async def main():
    origin = 'Geroiv Stalingradu,2g, Kyiv, Ukraine'
    destination = '4ROOM, Petropavlovskaya str,6, Kyiv region, 08130,Ukraine'
    now = datetime.datetime.now()
    min_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    max_time = now.replace(hour=18, minute=0, second=0, microsecond=0)

    if now > min_time and now < max_time:
        await send_route_message(destination, origin, 18)
    elif now < min_time:
        await send_route_message(origin, destination, 9)
    else:
        print("End")


if __name__ == '__main__':
    asyncio.run(main())
