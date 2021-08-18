import aiohttp
from nonebot.log import logger


async def get_pic_url(key_word='', r18=False) -> str:
    url = 'https://api.lolicon.app/setu/v2'
    params = {
        'r18': 1 if r18 else 0,
        'num': 1,
        'size': ['regular'],
        'proxy': 'i.pixiv.cat',
        'keyword': key_word
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            response = await resp.json()
    if response['error']:
        logger.warning('lolicon error: ' + response['error'])
        return ''
    result = response['data'][0]['urls']['regular']
    logger.info('Get setu url: ' + result)
    return result
