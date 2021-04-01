import aiohttp
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
setu_config = Config(**global_config.dict())


async def get_pic_url(key_word=None, r18=False) -> str:
    url = 'https://api.lolicon.app/setu/'
    data = {
        'apikey': setu_config.setu_apikey,
        'r18': 1 if r18 else 0,
        'num': 1,
        'size1200': 1,
        'keyword': key_word
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.json()
    if response['code'] != 0:
        return ''
    result = response['data'][0]['url']
    logger.info('Get setu url: ' + result)
    return result
