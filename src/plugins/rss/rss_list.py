import json
from pathlib import Path
from .rss_class import RSS

data_path = Path('data/rss')
if not data_path.exists():
    data_path.mkdir(parents=True)
rss_path = data_path / 'rss_list.json'


def _load_rss_list() -> dict:
    try:
        rss_list = {}
        json_list = json.load(rss_path.open('r', encoding='utf-8'))
        for user_id, user_rss_list in json_list.items():
            rss_list[user_id] = [RSS.from_json(rss) for rss in user_rss_list]
        return rss_list
    except FileNotFoundError:
        return {}


_rss_list = _load_rss_list()


def _dump_rss_list():
    rss_path.parent.mkdir(parents=True, exist_ok=True)
    json_list = {}
    for user_id, user_rss_list in _rss_list.items():
        json_list[user_id] = [rss.to_json() for rss in user_rss_list]
    json.dump(
        json_list,
        rss_path.open('w', encoding='utf-8'),
        indent=4,
        separators=(',', ': '),
        ensure_ascii=False
    )


def get_user_ids() -> list:
    return list(_rss_list.keys())


def get_rss_list(user_id: str) -> list:
    return _rss_list.get(user_id, {})


def add_rss_list(user_id: str, new_rss: RSS) -> str:
    user_sub_list = get_rss_list(user_id)
    names = [rss.name for rss in user_sub_list]
    if new_rss.name in names:
        return 'dupe'
    if user_id not in _rss_list:
        _rss_list[user_id] = []
    _rss_list[user_id].append(new_rss)
    _dump_rss_list()
    return 'success'


def del_rss_list(user_id: str, name: str) -> str:
    user_sub_list = get_rss_list(user_id)
    index = -1
    for rss in user_sub_list:
        if rss.name == name:
            index = user_sub_list.index(rss)
            break
    if index == -1:
        return 'dupe'
    user_sub_list.pop(index)
    _dump_rss_list()
    return 'success'


def clear_rss_list(user_id: str) -> str:
    _rss_list.pop(user_id)
    _dump_rss_list()
    return 'success'
