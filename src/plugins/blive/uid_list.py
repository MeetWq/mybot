import json
from pathlib import Path

uid_list_path = Path() / 'data' / 'blive' / 'uid_list.json'


def load_uid_list() -> dict:
    try:
        return json.load(uid_list_path.open('r', encoding='utf-8'))
    except FileNotFoundError:
        return {}


_uid_list = load_uid_list()


def dump_uid_list():
    uid_list_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        _uid_list,
        uid_list_path.open('w', encoding='utf-8'),
        indent=4,
        separators=(',', ': ')
    )


def get_sub_uids() -> list:
    return list(_uid_list)


def get_sub_users(uid: str) -> list:
    if uid not in _uid_list:
        return []
    return _uid_list[uid].get('sub_users', [])


def get_dynamic_users(uid: str) -> list:
    if uid not in _uid_list:
        return []
    return _uid_list[uid].get('dynamic_users', [])


def get_record_users(uid: str) -> list:
    if uid not in _uid_list:
        return []
    return _uid_list[uid].get('record_users', [])


def add_sub_user(user_id: str, uid: str):
    if uid not in _uid_list:
        _uid_list[uid] = {
            'sub_users': [user_id],
            'record_users': [],
            'dynamic_users': []
        }
    else:
        sub_users = get_sub_users(uid)
        sub_users.append(user_id)
        sub_users = list(set(sub_users))
        _uid_list[uid]['sub_users'] = sub_users
    dump_uid_list()


def del_sub_user(user_id: str, uid: str):
    if uid not in _uid_list:
        return
    sub_users = get_sub_users(uid)
    if user_id in sub_users:
        sub_users.remove(user_id)
    if not sub_users:
        _uid_list.pop(uid)
    else:
        _uid_list[uid]['sub_users'] = sub_users
    del_dynamic_user(user_id, uid)
    del_record_user(user_id, uid)
    dump_uid_list()


def add_dynamic_user(user_id: str, uid: str):
    if uid not in _uid_list:
        _uid_list[uid] = {
            'sub_users': [],
            'record_users': [],
            'dynamic_users': [user_id]
        }
    else:
        dynamic_users = get_dynamic_users(uid)
        dynamic_users.append(user_id)
        dynamic_users = list(set(dynamic_users))
        _uid_list[uid]['dynamic_users'] = dynamic_users
    dump_uid_list()


def del_dynamic_user(user_id: str, uid: str):
    if uid not in _uid_list:
        return
    dynamic_users = get_dynamic_users(uid)
    if user_id in dynamic_users:
        dynamic_users.remove(user_id)
    _uid_list[uid]['dynamic_users'] = dynamic_users
    dump_uid_list()


def add_record_user(user_id: str, uid: str):
    if uid not in _uid_list:
        _uid_list[uid] = {
            'sub_users': [user_id],
            'record_users': [user_id],
            'dynamic_users': []
        }
    else:
        record_users = get_record_users(uid)
        record_users.append(user_id)
        record_users = list(set(record_users))
        _uid_list[uid]['record_users'] = record_users
    dump_uid_list()


def del_record_user(user_id: str, uid: str):
    if uid not in _uid_list:
        return
    record_users = get_record_users(uid)
    if user_id in record_users:
        record_users.remove(user_id)
    _uid_list[uid]['record_users'] = record_users
    dump_uid_list()
