import json
import aiohttp


async def get_live_info(uid: str = '', up_name: str = '') -> dict:
    info = {}
    if uid:
        info = await get_live_info_by_uid(uid)
    elif up_name:
        info = await get_live_info_by_name(up_name)
    return info


async def get_live_info_by_uid(uid: str) -> dict:
    result = await get_live_info_by_uids([uid])
    if uid in result:
        return result[uid]
    return {}


async def get_live_info_by_uids(uids: list) -> dict:
    try:
        url = 'https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps({'uids': uids})) as resp:
                result = await resp.json()
        if not result or result['code'] != 0:
            return {}
        return result['data']
    except:
        return {}


async def get_live_info_by_name(up_name: str) -> dict:
    user_info = await get_user_info_by_name(up_name)
    if not user_info:
        return {}
    return await get_live_info_by_uid(str(user_info['mid']))


async def get_user_info_by_name(up_name: str) -> dict:
    try:
        url = 'http://api.bilibili.com/x/web-interface/search/type'
        params = {
            'search_type': 'bili_user',
            'keyword': up_name
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                result = await resp.json()
        if not result or result['code'] != 0:
            return {}
        users = result['data']['result']
        for user in users:
            if user['uname'] == up_name:
                return user
        return {}
    except:
        return {}


async def get_play_url(room_id: int) -> str:
    try:
        url = 'http://api.live.bilibili.com/room/v1/Room/playUrl'
        params = {
            'cid': room_id,
            'platform': 'web',
            'qn': 10000
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                result = await resp.json()
        if not result or result['code'] != 0:
            return ''
        return result['durl'][0]['url']
    except:
        return ''
