
"""NLP PART TEMP!"""

# text preprocessing
from pymorphy2 import MorphAnalyzer
import string
from stop_words import get_stop_words
import re
import json

# chat-bot creation
from gensim.models import Word2Vec, FastText
import gensim
import annoy

from tqdm.notebook import tqdm
import numpy as np

# import fuzz

from fuzzywuzzy import fuzz
from fuzzywuzzy import process


import logging

from aiogram import Bot, Dispatcher, executor, types

import config

import pars, random


with open("cities.txt", "r", encoding="utf-8") as file:
    city_list = file.readlines()[0].lower().split()
    file.close()

with open("film_frase.txt", "r", encoding="utf-8") as file:
    film_phrase = file.readlines()[0].lower().split(",")
    file.close()

"""Подгружаю модели""" 

print("Loading models...") 

with open('NLP/index_map.txt') as json_file:
    index_map = json.load(json_file)

#w2v_index = annoy.AnnoyIndex(300 ,'angular')
ft_index = annoy.AnnoyIndex(300 ,'angular')

print("Json - Done")

#w2v_index.load('w2v_index')
ft_index.load('NLP/ft_index')

print("Index - Done")


#modelW2V = Word2Vec.load('w2v_model') 
model_ft = FastText.load('NLP/ft_model')

print("Models - Done\n Loading complete!")
"""Готово""" 


morpher = MorphAnalyzer()
sw = set(get_stop_words("ru"))
exclude = set(string.punctuation)


def preprocess_txt(text):
    text = re.sub(r'<.*?>', ' ', text)
    text = re.sub(r'.*:', ' ', text)
    text = "".join(i for i in text.strip() if i not in exclude).split()
    # text = re.sub(fr'[{string.punctuation}]+', ' ', text)
    text = [morpher.parse(i.lower())[0].normal_form for i in text]
    text = [i for i in text if i not in sw and i != ""]
    return text


def get_response(question, index, model, index_map, count_answer=3):
    #question = preprocess_txt(question)
    vector = np.zeros(300)
    norm = 0
    for word in question:
        if word in model.wv:
            vector += model.wv[word]
            norm += 1
    if norm > 0:
        vector = vector / norm
    answers = index.get_nns_by_vector(vector, count_answer)
    unfiltered_answers = [index_map[str(i)] for i in answers]
    filtered_answers = [i for i in unfiltered_answers if len(i)<4000]
    text = random.choice(filtered_answers)
    text = re.sub(r'<.*?>', ' ', text)
    text = re.sub(r'.*:', ' ', text)
    return text
"""NLP PART TEMP!"""


def is_movie(text):
    max_fuzz = 0
    for i in film_phrase:
        if fuzz.ratio(text,i)>max_fuzz:
            max_fuzz=fuzz.ratio(text,i)

    if max_fuzz >=90:
        return True

    else:
        return False

API_TOKEN = config.TG_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def text_handler(text, text_raw):
    
    if "погода" in text:
        try:
            city = [i for i in text if i in city_list]
            return (f'О погоде...\n {pars.get_wheater(city[0],config.open_weather_token)}')
        except IndexError:
            return ("Ты по-моему что-то перепутал...")

    
    elif is_movie(text_raw):
        return (f'Попробуй посмотреть этот..\n{pars.random_film(config.kp_token)}\n\n Если уже смотрел, то посмотри еще раз!')

    else:
        return (get_response(text, ft_index, model_ft, index_map, count_answer=10))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer("Привет я бот говорун..\nНе отличаюсь умом и сообразительностью.")

@dp.message_handler()
async def not_a_comand(message: types.Message):
    """
    This handler will handle all text exept 
    """

    await message.answer(f'{text_handler(preprocess_txt(message.text),message.text)}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)