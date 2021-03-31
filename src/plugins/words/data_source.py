import os
import json
import random

dir_path = os.path.split(os.path.realpath(__file__))[0]


async def get_ussrjoke(thing, man, theory, victim, range):
    path = os.path.join(dir_path, 'ussr-jokes.json')
    with open(path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['jokes']).format(thing=thing, man=man, theory=theory, victim=victim, range=range)


async def get_cp_story(name_a, name_b):
    path = os.path.join(dir_path, 'cp-stories.json')
    with open(path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['stories']).format(A=name_a, B=name_b)


async def get_marketing_article(topic, description, another):
    path = os.path.join(dir_path, 'marketing-article.json')
    with open(path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['text']).format(topic=topic, description=description, another=another)
