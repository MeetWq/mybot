import itertools
import urllib.parse
from typing import Optional

import httpx
import wolframalpha
from nonebot.log import logger

from .config import wolframalpha_config


async def get_wolframalpha_simple(input, params=(), **kwargs) -> Optional[bytes]:
    data = {
        "input": input,
        "appid": wolframalpha_config.wolframalpha_appid,
    }
    data = itertools.chain(params, data.items(), kwargs.items())
    query = urllib.parse.urlencode(tuple(data))
    url = "https://api.wolframalpha.com/v2/simple?" + query

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            return resp.content
    except Exception as e:
        logger.warning(f"Error in get_wolframalpha_simple({input}): {e}")


async def get_wolframalpha_text(input, params=(), **kwargs) -> str:
    try:
        client = wolframalpha.Client(wolframalpha_config.wolframalpha_appid)
        res = client.query(input, params, **kwargs)
        return next(res.results).text
    except Exception as e:
        logger.warning(f"Error in get_wolframalpha_text({input}): {e}")
        return ""
