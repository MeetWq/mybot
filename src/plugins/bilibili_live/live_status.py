import json
from pathlib import Path

from .data_source import get_live_info
from .sub_list import load_sub_list

status_path = Path() / 'data' / 'bilibili_live' / 'live_status.json'


def get_status(room_id: str) -> dict:
    status_list = load_status_list()
    if room_id not in status_list:
        return 0
    return status_list[room_id]


def update_status(room_id: str, status: int) -> dict:
    status_list = load_status_list()
    status_list[room_id] = status
    dump_status_list(status_list)


def load_status_list() -> dict:
    try:
        return json.load(status_path.open('r', encoding='utf-8'))
    except FileNotFoundError:
        return {}


def dump_status_list(status_list: dict):
    status_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        status_list,
        status_path.open('w', encoding='utf-8'),
        indent=4,
        separators=(',', ': ')
    )


async def update_status_list():
    sub_list = load_sub_list()
    user_list = set()
    for group_sub_list in sub_list.values():
        for room_id in group_sub_list.keys():
            user_list.add(room_id)
    status_list = load_status_list()
    room_ids = list(status_list.keys())
    for room_id in room_ids:
        if room_id not in user_list:
            status_list.pop(room_id)
    for room_id in user_list:
        if room_id not in status_list:
            info = await get_live_info(room_id)
            status = info['status']
            status_list[room_id] = status
    dump_status_list(status_list)
