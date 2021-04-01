import re
import random
import aiohttp
import traceback
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote

from nonebot.log import logger

image_path = Path('src/data/images')


def get_emoji_path(name: str):
    patterns = [
        (r'(ac\d{2,4})', 'ac', lambda x: x.group(1)),
        (r'(em\d{2})', 'em', lambda x: x.group(1)),
        (r'emm(\d{1,3})', 'nhd', lambda x: 'em' + x.group(1)),
        (r'([acf]:?\d{3})', 'mahjong', lambda x: x.group(1)),
        (r'(ms\d{2})', 'ms', lambda x: x.group(1)),
        (r'(tb\d{2})', 'tb', lambda x: x.group(1)),
        (r'([Cc][Cc]98\d{2})', 'cc98', lambda x: x.group(1))
    ]

    name = name.strip().split('.')[0].replace(':', '').lower()
    file_ext = ['.jpg', '.png', '.gif']
    for pattern, dir_name, func in patterns:
        if re.match(pattern, name):
            name = re.sub(pattern, func, name)
            for ext in file_ext:
                file_path = image_path / dir_name / (name + ext)
                if file_path.exists():
                    return str(file_path.absolute())
    return None


async def get_image(keyword):
    url = f'https://fabiaoqing.com/search/bqb/keyword/{quote(keyword)}/type/bq/page/1.html'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = await resp.text()

    result = BeautifulSoup(result, 'lxml')
    images = result.find_all('div', {'class': 'searchbqppdiv tagbqppdiv'})
    image_num = len(images)
    if image_num <= 0:
        return ''
    if image_num >= 3:
        images = images[:3]
    return random.choice(images).img['data-original']
