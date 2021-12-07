import json
from pathlib import Path

from .uid_list import add_sub_user, del_sub_user, add_record_user, del_record_user, add_dynamic_user, del_dynamic_user

data_path = Path() / 'data' / 'blive' / 'sub_list.json'


def load_sub_list() -> dict:
    try:
        return json.load(data_path.open('r', encoding='utf-8'))
    except FileNotFoundError:
        return {}


_sub_list = load_sub_list()


def dump_sub_list():
    data_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        _sub_list,
        data_path.open('w', encoding='utf-8'),
        indent=4,
        separators=(',', ': '),
        ensure_ascii=False
    )


def get_sub_list(user_id: str) -> dict:
    if user_id not in _sub_list:
        return {}
    return _sub_list[user_id]


def add_sub_list(user_id: str, uid: str, info: dict) -> str:
    sub_list = get_sub_list(user_id)
    if uid in sub_list:
        return 'dupe'
    sub_list[uid] = {
        'up_name': info['uname'],
        'room_id': info['room_id'],
        'record': False,
        'dynamic': False
    }
    _sub_list[user_id] = sub_list
    dump_sub_list()
    add_sub_user(user_id, uid)
    return 'success'


def del_sub_list(user_id: str, uid: str) -> str:
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        return 'dupe'
    sub_list.pop(uid)
    if sub_list:
        _sub_list[user_id] = sub_list
    else:
        _sub_list.pop(user_id)
    dump_sub_list()
    del_sub_user(user_id, uid)
    return 'success'


def clear_sub_list(user_id: str) -> str:
    if user_id in _sub_list:
        for uid in _sub_list[user_id].keys():
            del_sub_user(user_id, uid)
        _sub_list.pop(user_id)
    dump_sub_list()
    return 'success'


def open_dynamic(user_id: str, uid: str) -> str:
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        return 'dupe'
    _sub_list[user_id][uid]['dynamic'] = True
    dump_sub_list()
    add_dynamic_user(user_id, uid)
    return 'success'


def close_dynamic(user_id: str, uid: str) -> str:
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        return 'dupe'
    _sub_list[user_id][uid]['dynamic'] = False
    dump_sub_list()
    del_dynamic_user(user_id, uid)
    return 'success'


def open_record(user_id: str, uid: str) -> str:
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        return 'dupe'
    _sub_list[user_id][uid]['record'] = True
    dump_sub_list()
    add_record_user(user_id, uid)
    return 'success'


def close_record(user_id: str, uid: str) -> str:
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        return 'dupe'
    _sub_list[user_id][uid]['record'] = False
    dump_sub_list()
    del_record_user(user_id, uid)
    return 'success'
