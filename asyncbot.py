
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

# translation
from transformers import FSMTForConditionalGeneration, FSMTTokenizer
from langdetect import detect

from tqdm.notebook import tqdm
import numpy as np

from fuzzywuzzy import fuzz, process

import logging

from aiogram import Bot, Dispatcher, executor, types

import config

import pars, random

"""Loading text files""" 

with open("TXT/cities.txt", "r", encoding="utf-8") as file:
    city_list = file.readlines()[0].lower().split()
    file.close()

with open("TXT/film_frase.txt", "r", encoding="utf-8") as file:
    film_phrase = file.readlines()[0].lower().split(",")
    file.close()

with open("TXT/bye.txt", "r", encoding="utf-8") as file:
    bye = file.readlines()[0].lower().split(",")
    file.close()

"""Loading Models""" 

print("Loading models...") 

with open('NLP/index_map.txt') as json_file:
    index_map = json.load(json_file)

w2v_index = annoy.AnnoyIndex(300 ,'angular')
ft_index = annoy.AnnoyIndex(300 ,'angular')

print("Json - Done")

w2v_index.load('NLP/w2v_index')
ft_index.load('NLP/ft_index')

print("Index - Done")


modelW2V = Word2Vec.load('NLP/w2v_model') 
model_ft = FastText.load('NLP/ft_model')

# с англ на рус
en_model = "facebook/wmt19-en-ru"
# с рус на англ
ru_model = "facebook/wmt19-ru-en"

tokenizer_en = FSMTTokenizer.from_pretrained(en_model)
tokenizer_ru = FSMTTokenizer.from_pretrained(ru_model)
en_to_ru = FSMTForConditionalGeneration.from_pretrained(en_model)
ru_to_en = FSMTForConditionalGeneration.from_pretrained(ru_model)

print("Translate - Done")

print("Models - Done\n Loading complete!")
"""Ready""" 


morpher = MorphAnalyzer()
sw = set(get_stop_words("ru"))
exclude = set(string.punctuation)


def preprocess_txt(text):
    text = re.sub(r'<.*?>', ' ', text)
    text = re.sub(r'.*:', ' ', text)
    text = "".join(i for i in text.strip() if i not in exclude).split()
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


def is_phrase(text, phrases):
    max_fuzz = 0
    text = text.lower()
    for i in phrases:
        if fuzz.ratio(text,i)>max_fuzz:
            max_fuzz=fuzz.ratio(text,i)

    if max_fuzz >=90:
        return True

    else:
        return False


def translator(text, tokenizer, model):

    inputs = tokenizer.encode(text, return_tensors="pt")
    outputs = model.generate(inputs)
    translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return translation


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

    
    elif is_phrase(text_raw, film_phrase):
        return (f'Попробуй посмотреть этот..\n{pars.random_film(config.kp_token)}\n\n Если уже смотрел, то посмотри еще раз!')

    elif is_phrase(text_raw, bye):
        return "Всего хорошего!"
    
    elif "переведи" in text_raw.lower().split():
        text_to_translate = text_raw.split()[1:]
        text_to_translate = ' '.join(text_to_translate)
        lang = detect(text_to_translate)
        if lang == 'en':
            return translator(text_to_translate, tokenizer_en, en_to_ru)
        else:
            return translator(text_to_translate, tokenizer_ru, ru_to_en)
      
    else:
        return (get_response(text, ft_index, model_ft, index_map, count_answer=7))
        # return (get_response(text, w2v_index, modelW2V, index_map, count_answer=7))


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