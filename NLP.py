"""
Hello this is NLP.py

I`am glad to see you! Rightnow im in development state, and may look kinda dumb.

"""
#Add more sense to description

#import - don`t forget to create requirements.txt

import logging

from aiogram import Bot, Dispatcher, executor, types

import pars, config

def text_handler(text):

    if "погода" in text.split():
        return (f'О погоде...\n {pars.get_wheater(text.split()[-1],config.open_weather_token)}')
    
    elif "фильм" in text.split():
        return (f'Попробуй посмотреть этот..\n{pars.random_film(config.kp_token)}\n\n Если уже смотрел, то посмотри еще раз!')
    else:
        return (f"Кеша: {text}")
