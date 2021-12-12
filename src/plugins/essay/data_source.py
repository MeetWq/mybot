import json
import httpx
import random
from pathlib import Path
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
essay_config = Config(**global_config.dict())

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


async def get_chicken_soup():
    path = data_path / 'soups.json'
    with path.open('r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['soups'])


async def get_head_poem(keyword: str):
    url = 'http://api.yanxi520.cn/api/betan.php'
    params = {
        'b': random.choice([5, 7]),
        'a': 1,
        'msg': keyword
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, params=params)
            result = resp.text
        return result
    except Exception as e:
        logger.warning(f"Error in get_head_poem({keyword}): {e}")
        return ''
