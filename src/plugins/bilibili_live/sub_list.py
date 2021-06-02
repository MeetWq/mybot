import json
from pathlib import Path

data_path = Path() / 'data' / 'bilibili_live' / 'sub_list.json'


def get_sub_list(user_id: str) -> dict:
    sub_list = load_sub_list()
    if user_id not in sub_list:
        return {}
    return sub_list[user_id]


def add_sub_list(user_id: str, room_id: str, up_name: str) -> str:
    sub_list = load_sub_list()
    group_sub_list = {}
    if user_id in sub_list:
        group_sub_list = sub_list[user_id]
    if room_id in group_sub_list:
        return 'dupe'
    group_sub_list[room_id] = up_name
    sub_list[user_id] = group_sub_list
    dump_sub_list(sub_list)
    return 'success'


def del_sub_list(user_id: str, room_id: str) -> str:
    sub_list = load_sub_list()
    group_sub_list = {}
    if user_id in sub_list:
        group_sub_list = sub_list[user_id]
    if room_id not in group_sub_list:
        return 'dupe'
    group_sub_list.pop(room_id)
    if group_sub_list:
        sub_list[user_id] = group_sub_list
    else:
        sub_list.pop(user_id)
    dump_sub_list(sub_list)
    return 'success'


def clear_sub_list(user_id: str) -> str:
    sub_list = load_sub_list()
    sub_list.pop(user_id)
    dump_sub_list(sub_list)
    return 'success'


def load_sub_list() -> dict:
    try:
        return json.load(data_path.open('r', encoding='utf-8'))
    except FileNotFoundError:
        return {}


def dump_sub_list(sub_list: dict):
    data_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        sub_list,
        data_path.open('w', encoding='utf-8'),
        indent=4,
        separators=(',', ': '),
        ensure_ascii=False
    )
