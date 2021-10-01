import requests
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


# async def get_play_url(room_id: str) -> str:
#     try:
#         live = LiveRoom(int(room_id))
#         play_url = await live.get_room_play_url()
#         url = play_url['durl'][0]['url']
#         return url
#     except (ApiException, AttributeError, KeyError):
#         return ''


def get_play_url(room_id: str) -> str:
    try:
        live = LiveRoom(int(room_id))
        api = 'https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl'
        params = {
            'cid': live.room_display_id,
            'platform': 'web',
            'qn': 10000,
            'https_url_req': '1',
            'ptype': '16'
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'referer': 'https://live.bilibili.com/'
        }
        return requests.get(api, params=params, headers=headers).json()['data']['durl'][0]['url']
    except:
        return ''


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
