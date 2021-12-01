import json
import aiohttp
import traceback
from nonebot.log import logger
from datetime import datetime, timedelta


async def get_dynmap_updates(url: str):
    try:
        stamp = (datetime.now() - timedelta(minutes=2)).timestamp()
        url += '/' + str(int(stamp * 1000))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.read()
        result = json.loads(result)
        return result
    except:
        logger.debug(traceback.format_exc())
        return None


async def get_status(url: str) -> str:
    result = await get_dynmap_updates(url)
    if not result:
        return ''
    players = result['players']
    players = [p['account'] for p in players]
    players = ', '.join(players)
    tick = result['servertime']
    tick = tick - 18000
    tick = tick + 24000 if tick < 0 else tick
    tick = tick * 36
    stime = '{:02d}:{:02d}:{:02d}.{:01d}'.format(
        tick // 10 // 60 // 60,
        tick // 10 // 60 % 60,
        tick // 10 % 60,
        tick % 10
    )
    storm = result['hasStorm']
    thunder = result['isThundering']
    weather = '☀' if not storm else '⛈' if thunder else '🌧'
    status = f'当前在线：{players}\n服务器时间：{stime}\n服务器天气：{weather}'
    return status


async def send_message(config, msg):
    try:
        login_url = config['url'] + '/up/login'
        send_url = config['url'] + '/up/sendmessage'
        info = {
            'j_username': config['username'],
            'j_password': config['password']
        }
        data = {
            'name': '',
            'message': msg
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(login_url, data=info) as resp:
                if resp.status != 200:
                    return False
            async with session.post(send_url, json=data) as resp:
                if resp.status != 200:
                    return False
        return True
    except:
        logger.debug(traceback.format_exc())
        return False
