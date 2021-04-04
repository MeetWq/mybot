import bilibili_api
from datetime import datetime
from bilibili_api import live, user
from bilibili_api.exceptions import BilibiliException


async def get_live_info(room_id: str='', up_name: str='') -> dict:
    if room_id:
        info = await get_live_info_by_id(room_id)
    elif up_name:
        info = await get_live_info_by_name(up_name)
    else:
        info = {}
    return info


async def get_live_info_by_id(room_id: str) -> dict:
    try:
        data = live.get_room_info(room_id)['room_info']
        uid = data['uid']
        up_info = await get_user_info(uid)
        time = data['live_start_time']
        time = datetime.fromtimestamp(time).strftime("%y/%m/%d %H:%M:%S")
        info = {
            'status': data['live_status'],
            'uid': str(data['uid']),
            'room_id': str(data['room_id']),
            'up_name': up_info['name'],
            'url': 'https://live.bilibili.com/%s' % data['room_id'],
            'title': data['title'],
            'time': time,
            'cover': data['cover']
        }
        return info
    except (BilibiliException, AttributeError, KeyError):
        return {}


async def get_live_info_by_name(up_name: str) -> dict:
    try:
        result = bilibili_api.web_search_by_type(keyword=up_name, search_type='bili_user')
        users = result['result']
        if not users:
            return {}
        for user in users:
            if user['uname'] == up_name:
                room_id = user['room_id']
                info = await get_live_info_by_id(room_id)
                return info
        return {}
    except (BilibiliException, AttributeError, KeyError):
        return {}


async def get_user_info(uid: str) -> dict:
    try:
        data = user.get_user_info(uid)
        info = {
            'name': data['name'],
            'sex': data['sex'],
            'face': data['face'],
            'sign': data['sign']
        }
        return info
    except (BilibiliException, AttributeError, KeyError):
        return {}
