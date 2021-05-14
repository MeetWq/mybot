import base64
import aiohttp
import itertools
import urllib.parse
import wolframalpha
from nonebot import get_driver
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

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.read()
                return MessageSegment.image(f"base64://{base64.b64encode(data).decode()}")
            else:
                return None


async def get_wolframalpha_text(input, params=(), **kwargs):
    try:
        client = wolframalpha.Client(wolframalpha_config.wolframalpha_appid)
        res = client.query(input, params, **kwargs)
        return next(res.results).text
    except:
        return ''
