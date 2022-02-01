import json
from typing import Dict
from pathlib import Path

from .uid_list import update_uid_list

data_path = Path() / 'data' / 'blive' / 'sub_list.json'


class DupeError(Exception):
    pass


def load_sub_list() -> Dict[str, Dict[str, dict]]:
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


def get_sub_list(user_id: str) -> Dict[str, dict]:
    if user_id not in _sub_list:
        return {}
    return _sub_list[user_id]


def add_sub_list(user_id: str, uid: str, info: dict):
    sub_list = get_sub_list(user_id)
    if uid in sub_list:
        raise DupeError
    sub_list[uid] = {
        'up_name': info['uname'],
        'room_id': info['room_id'],
        'record': False,
        'dynamic': False
    }
    _sub_list[user_id] = sub_list
    dump_sub_list()
    update_uid_list(_sub_list)


def del_sub_list(user_id: str, uid: str):
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        raise DupeError
    sub_list.pop(uid)
    if sub_list:
        _sub_list[user_id] = sub_list
    else:
        _sub_list.pop(user_id)
    dump_sub_list()
    update_uid_list(_sub_list)


def clear_sub_list(user_id: str):
    if user_id in _sub_list:
        _sub_list.pop(user_id)
    dump_sub_list()
    update_uid_list(_sub_list)


def open_dynamic(user_id: str, uid: str):
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        raise DupeError
    _sub_list[user_id][uid]['dynamic'] = True
    dump_sub_list()
    update_uid_list(_sub_list)


def close_dynamic(user_id: str, uid: str):
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        raise DupeError
    _sub_list[user_id][uid]['dynamic'] = False
    dump_sub_list()
    update_uid_list(_sub_list)


def open_record(user_id: str, uid: str):
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        raise DupeError
    _sub_list[user_id][uid]['record'] = True
    dump_sub_list()
    update_uid_list(_sub_list)


def close_record(user_id: str, uid: str):
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        raise DupeError
    _sub_list[user_id][uid]['record'] = False
    dump_sub_list()
    update_uid_list(_sub_list)
