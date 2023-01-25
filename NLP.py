"""
Hello this is NLP.py

I`am glad to see you! Rightnow im in development state, and may look kinda dumb.

"""
#Add more sense to description

#import - don`t forget to create requirements.txt

import logging

from aiogram import Bot, Dispatcher, executor, types

import weather_step, config

def text_handler(text):

    if "погода" in text.split():
        return (f'О погоде...\n {weather_step.get_wheater(text.split()[-1],config.open_weather_token)}')
    
    else:
        return (f"Кеша -  {text}")