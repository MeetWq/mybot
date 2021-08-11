import aiohttp
from datetime import datetime, timedelta


async def get_dynmap_updates(url: str):
    try:
        stamp = (datetime.now() - timedelta(minutes=1)).timestamp()
        url += '/' + str(int(stamp * 1000))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.json()
        return result
    except:
        return None


async def get_status(url: str) -> str:
    result = await get_dynmap_updates(url)
    players = result['players']
    players = [p['account'] for p in players]
    players = ', '.join(players)
    time = result['servertime']
    time = int(time / 20)
    time = f'{time // 60}:{time % 60}'
    storm = result['hasStorm']
    thunder = result['isThundering']
    weather = '☀' if not storm else '⛈' if thunder else '🌧'
    status = f'当前在线：{players}\n服务器时间：{time}\n服务器天气：{weather}'
    return status
