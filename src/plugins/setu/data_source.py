import base64
import aiohttp
import traceback
from nonebot.log import logger
from nonebot.adapters.cqhttp import Message, MessageSegment


async def get_setu(key_word='', r18=False) -> Message:
    url = 'https://api.lolicon.app/setu/v2'
    params = {
        'r18': 1 if r18 else 0,
        'num': 1,
        'size': ['regular'],
        'proxy': 'i.pixiv.cat',
        'keyword': key_word
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                response = await resp.json()
        if response['error']:
            logger.warning('lolicon error: ' + response['error'])
            return None
        if response['data']:
            setu_url = response['data'][0]['urls']['regular']
            logger.info('Get setu url: ' + setu_url)

            async with aiohttp.ClientSession() as session:
                async with session.get(setu_url) as resp:
                    result = await resp.read()

            if result:
                return MessageSegment.image(f"base64://{base64.b64encode(result).decode()}")
            return None
        else:
            return '找不到相关的涩图'
    except:
        logger.warning(traceback.format_exc())
        return None
