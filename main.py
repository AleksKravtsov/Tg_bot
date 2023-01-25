from config import open_weather_token
import requests
import datetime
from pprint import pprint

def get_wheater(city, open_weather_token):
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        # pprint(data)

        city = data['name']
        cur_weather = data['main']['temp']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind = data['wind']['speed']

        print(f'***{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}***\n'
              f'Погода в городе: {city}\nТемпература: {cur_weather}C°\n'
              f'Влажность: {humidity}\nДавление: {pressure} мм.рт.ст\n'
              f'Скорость ветра: {wind} м/c')


    except Exception as ex:
        print(ex)
        print('Проверьте название города')


def main():
    city = input('Введите город: ')
    get_wheater(city, open_weather_token)
    pass


if __name__ == '__main__':
    main()