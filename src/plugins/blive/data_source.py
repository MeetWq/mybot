from datetime import datetime
from bilibili_api.live import LiveRoom
from bilibili_api.user import User
from bilibili_api.exceptions import ApiException
from bilibili_api.utils.network import request
from bilibili_api.utils.utils import get_api


async def get_live_info(room_id: str = '', up_name: str = '') -> dict:
    if room_id:
        info = await get_live_info_by_id(room_id)
    elif up_name:
        info = await get_live_info_by_name(up_name)
    else:
        info = {}
    return info


async def get_live_info_by_id(room_id: str) -> dict:
    try:
        live = LiveRoom(int(room_id))
        room_info = await live.get_room_info()
        data = room_info['room_info']
        uid = data['uid']
        up_info = await get_user_info(str(uid))
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
    except (ApiException, AttributeError, KeyError):
        return {}


async def get_live_info_by_name(up_name: str) -> dict:
    try:
        api = get_api('common')['search']['web_search_by_type']
        params = {'keyword': up_name, 'search_type': 'bili_user'}
        result = await request('GET', url=api['url'], params=params)
        users = result['result']
        if not users:
            return {}
        for user in users:
            if user['uname'] == up_name:
                room_id = user['room_id']
                info = await get_live_info_by_id(room_id)
                return info
        return {}
    except (ApiException, AttributeError, KeyError):
        return {}


async def get_live_status(room_id: str) -> int:
    try:
        live = LiveRoom(int(room_id))
        room_info = await live.get_room_info()
        return room_info['room_info']['live_status']
    except (ApiException, AttributeError, KeyError):
        return 0


async def get_user_info(uid: str) -> dict:
    try:
        user = User(int(uid))
        data = await user.get_user_info()
        info = {
            'name': data['name'],
            'sex': data['sex'],
            'face': data['face'],
            'sign': data['sign']
        }
        return info
    except (ApiException, AttributeError, KeyError):
        return {}
