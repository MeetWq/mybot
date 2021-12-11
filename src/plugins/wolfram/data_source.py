import httpx
import itertools
import urllib.parse
import wolframalpha
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.cqhttp import MessageSegment

from .config import Config

global_config = get_driver().config
wolframalpha_config = Config(**global_config.dict())


async def get_wolframalpha_simple(input, params=(), **kwargs):
    data = dict(
        input=input,
        appid=wolframalpha_config.wolframalpha_appid,
    )
    data = itertools.chain(params, data.items(), kwargs.items())
    query = urllib.parse.urlencode(tuple(data))
    url = 'https://api.wolframalpha.com/v2/simple?' + query

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            result = resp.content
        return MessageSegment.image(result)
    except Exception as e:
        logger.warning(f"Error in get_wolframalpha_simple({input}): {e}")
        return None


async def get_wolframalpha_text(input, params=(), **kwargs):
    try:
        client = wolframalpha.Client(wolframalpha_config.wolframalpha_appid)
        res = client.query(input, params, **kwargs)
        return next(res.results).text
    except Exception as e:
        logger.warning(f"Error in get_wolframalpha_text({input}): {e}")
        return ''
