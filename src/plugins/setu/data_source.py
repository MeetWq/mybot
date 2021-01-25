import os
import requests
import traceback
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
setu_config = Config(**global_config.dict())


async def get_pic_url(key_word=None) -> str:
    data = {
        'apikey': setu_config.setu_apikey,
        'r18': 0,
        'num': 1,
        'size1200': 1,
        'keyword': key_word
    }
    response = requests.get('https://api.lolicon.app/setu/', params=data).json()
    if response['code'] != 0:
        logger.warning('Error getting setu! ' + traceback.format_exc())
        return ''
    return response['data'][0]['url']


async def download_image(img_url: str, img_path: str):
    try:
        if not os.path.exists(img_path):
            r = requests.get(img_url)
            with open(img_path, 'wb') as f:
                f.write(r.content)
            return True
    except requests.exceptions:
        logger.warning('Error downloading image! ' + traceback.format_exc())
        return False
