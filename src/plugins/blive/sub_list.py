import json
from pathlib import Path

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


def get_sub_list(user_id: str = '') -> dict:
    if not user_id:
        return _sub_list.copy()
    if user_id not in _sub_list:
        return {}
    return _sub_list[user_id]


def add_sub_list(user_id: str, room_id: str, up_name: str) -> str:
    group_sub_list = {}
    if user_id in _sub_list:
        group_sub_list = _sub_list[user_id]
    if room_id in group_sub_list:
        return 'dupe'
    group_sub_list[room_id] = {
        'up_name': up_name,
        'record': False
    }
    _sub_list[user_id] = group_sub_list
    dump_sub_list()
    return 'success'


def del_sub_list(user_id: str, room_id: str) -> str:
    group_sub_list = {}
    if user_id in _sub_list:
        group_sub_list = _sub_list[user_id]
    if room_id not in group_sub_list:
        return 'dupe'
    group_sub_list.pop(room_id)
    if group_sub_list:
        _sub_list[user_id] = group_sub_list
    else:
        _sub_list.pop(user_id)
    dump_sub_list()
    return 'success'


def clear_sub_list(user_id: str) -> str:
    if user_id in _sub_list:
        _sub_list.pop(user_id)
    dump_sub_list()
    return 'success'


def open_record(user_id: str, room_id: str) -> str:
    _sub_list[user_id][room_id]['record'] = True
    dump_sub_list()
    return 'success'


def close_record(user_id: str, room_id: str) -> str:
    _sub_list[user_id][room_id]['record'] = False
    dump_sub_list()
    return 'success'
