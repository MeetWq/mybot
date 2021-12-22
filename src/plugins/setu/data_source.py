import httpx
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.cqhttp import Message, MessageSegment

global_config = get_driver().config
httpx_proxy = {
    'http://': global_config.http_proxy,
    'https://': global_config.http_proxy
}


async def get_setu(key_word='', r18=False) -> Message:
    url = 'https://api.lolicon.app/setu/v2'
    params = {
        'r18': 1 if r18 else 0,
        'num': 1,
        'size': ['regular'],
        'proxy': 'i.pixiv.re',
        'keyword': key_word
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

            if result:
                return MessageSegment.image(result)
            return None
        else:
            return '找不到相关的涩图'
    except Exception as e:
        logger.warning(f"Error in get_setu({key_word}): {e}")
        return None
