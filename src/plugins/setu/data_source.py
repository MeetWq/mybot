import requests
import traceback
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
setu_config = Config(**global_config.dict())


async def get_pic_url(key_word=None, r18=False) -> str:
    data = {
        'apikey': setu_config.setu_apikey,
        'r18': 1 if r18 else 0,
        'num': 1,
        'size1200': 1,
        'keyword': key_word
    }
    try:
        response = requests.get('https://api.lolicon.app/setu/', params=data, timeout=5).json()
        if response['code'] != 0:
            logger.warning('Error getting setu! ' + traceback.format_exc())
            return ''
        url = response['data'][0]['url']
        logger.info('Get setu url: ' + url)
        return url
    except requests.exceptions.RequestException:
        logger.warning('Error getting setu! ' + traceback.format_exc())
        return ''
