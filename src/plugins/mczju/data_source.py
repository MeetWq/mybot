from datetime import datetime, timedelta

import httpx
from nonebot.log import logger

from .config import mczju_config


async def get_dynmap_update():
    url = mczju_config.mczju_dynmap_url
    stamp = (datetime.now() - timedelta(minutes=2)).timestamp()
    url += "/" + str(int(stamp * 1000))
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            return resp.json()
    except Exception as e:
        logger.warning(f"Error in get_dynmap_updates({url}): {e}")


async def get_dynmap_status():
    result = await get_dynmap_update()
    if not result:
        return
    players = result["players"]
    players = [p["account"] for p in players]
    tick = result["servertime"]
    tick = tick - 18000
    tick = tick + 24000 if tick < 0 else tick
    tick = tick * 36
    hour = tick // 10 // 60 // 60
    minute = tick // 10 // 60 % 60
    second = tick // 10 % 60
    tick = tick % 10
    stime = f"{hour:02d}:{minute:02d}:{second:02d}.{tick:01d}"
    storm = result["hasStorm"]
    thunder = result["isThundering"]
    weather = "☀" if not storm else "⛈" if thunder else "🌧"
    return f"当前在线：{', '.join(players)}\n服务器时间：{stime}\n服务器天气：{weather}"
