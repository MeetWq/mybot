import json
from pathlib import Path

from .data_source import get_live_status
from .sub_list import get_sub_list

status_path = Path() / 'data' / 'blive' / 'live_status.json'


def load_status_list() -> dict:
    try:
        return json.load(status_path.open('r', encoding='utf-8'))
    except FileNotFoundError:
        return {}


_status_list = load_status_list()


def dump_status_list():
    status_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        _status_list,
        status_path.open('w', encoding='utf-8'),
        indent=4,
        separators=(',', ': ')
    )


def get_status_list() -> dict:
    return _status_list.copy()


def get_status(room_id: str) -> dict:
    if room_id not in _status_list:
        return 0
    return _status_list[room_id]


def update_status(room_id: str, status: int) -> dict:
    _status_list[room_id] = status
    dump_status_list()


async def update_status_list():
    sub_list = get_sub_list()
    room_list = set()
    for user_sub_list in sub_list.values():
        for room_id in user_sub_list.keys():
            room_list.add(room_id)

    room_ids = list(_status_list.keys())
    for room_id in room_ids:
        if room_id not in room_list:
            _status_list.pop(room_id)

    for room_id in room_list:
        if room_id not in _status_list:
            status = await get_live_status(room_id)
            _status_list[room_id] = status
    dump_status_list()
