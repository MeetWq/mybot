import httpx
from typing import Union
from nonebot.log import logger


async def get_setu(keyword='', r18=False) -> Union[str, bytes]:
    url = 'https://api.lolicon.app/setu/v2'
    params = {
        'r18': 1 if r18 else 0,
        'num': 1,
        'size': ['regular'],
        'proxy': 'i.pixiv.re',
        'keyword': keyword
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=20)
            result = resp.json()
        if result['error']:
            logger.warning('lolicon error: ' + result['error'])
            return None
        if result['data']:
            setu_url = result['data'][0]['urls']['regular']
            logger.info('Get setu url: ' + setu_url)

            async with httpx.AsyncClient() as client:
                resp = await client.get(setu_url, timeout=20)
                result = resp.content
            return result
        else:
            return '找不到相关的涩图'
    except Exception as e:
        logger.warning(f"Error in get_setu({keyword}): {e}")
        return None
