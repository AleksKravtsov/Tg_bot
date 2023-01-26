from config import open_weather_token
import requests
import datetime
from pprint import pprint
import requests
import random

api_link = "https://api.kinopoisk.dev/"



def random_film(kp_token):

    r = random.randrange(1,3000,1)
    params = {
        "token":kp_token,
        "field":["rating.kp","year"],
        "search":["7-9","2018-2022"],
        "limit":1,
        "page":r
        }

    response = requests.get(api_link+"movie", params=params)
    film = response.json()
    return "https://www.kinopoisk.ru/film/"+str(film["docs"][0]["id"])

def get_wheater(city, open_weather_token):
    
    code_to_smile = {
        'Clear': 'Ясно \U00002600',
        'Clouds': 'Облачно \U00002601',
        'Rain': 'Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U000026A1',
        'Snow': 'Снег \U0001F328',
        'Mist': 'Туман \U0001F32B'
    }
    
    
    
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        # pprint(data)

        city = data['name']
        cur_weather = data['main']['temp']

        weather_description = data['weather'][0]['main']
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = 'А фиг его знает, что там, глянть в окно:)'


        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind = data['wind']['speed']

        return(f'***{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}***\n'
              f'Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n'
              f'Влажность: {humidity}\nДавление: {pressure} мм.рт.ст\n'
              f'Скорость ветра: {wind} м/c')


    except Exception as ex:
        print(ex)
        return('Проверьте название города')
