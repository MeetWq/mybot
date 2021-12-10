import json
import random
from pathlib import Path

dir_path = Path(__file__).parent
data_path = dir_path / 'resources'


async def get_ussrjoke(thing, man, theory, victim, range):
    path = data_path / 'ussr-jokes.json'
    with path.open('r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['jokes']).format(thing=thing, man=man, theory=theory, victim=victim, range=range)


async def get_cp_story(name_a, name_b):
    path = data_path / 'cp-stories.json'
    with path.open('r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['stories']).format(A=name_a, B=name_b)


async def get_marketing_article(topic, description, another):
    path = data_path / 'marketing-article.json'
    with path.open('r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['text']).format(topic=topic, description=description, another=another)
