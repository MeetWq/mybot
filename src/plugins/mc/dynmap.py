import json
import aiohttp
import traceback
from nonebot.log import logger
from datetime import datetime, timedelta


async def get_dynmap_updates(url: str):
    try:
        stamp = (datetime.now() - timedelta(minutes=1)).timestamp()
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
    time = result['servertime']
    time = int(time / 20)
    time = '{:02d}:{:02d}'.format(time // 60, time % 60)
    storm = result['hasStorm']
    thunder = result['isThundering']
    weather = '☀' if not storm else '⛈' if thunder else '🌧'
    status = f'当前在线：{players}\n服务器时间：{time}\n服务器天气：{weather}'
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
