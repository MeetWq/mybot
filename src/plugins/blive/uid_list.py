import json
from pathlib import Path
from typing import Dict

uid_list_path = Path() / "data" / "blive" / "uid_list.json"


def load_uid_list() -> Dict[str, dict]:
    try:
        return json.load(uid_list_path.open("r", encoding="utf-8"))
    except FileNotFoundError:
        return {}


_uid_list = load_uid_list()


def dump_uid_list():
    uid_list_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(
        _uid_list,
        uid_list_path.open("w", encoding="utf-8"),
        indent=4,
        separators=(",", ": "),
        ensure_ascii=False,
    )


def get_sub_uids() -> list:
    return list(_uid_list)


def get_sub_users(uid: str) -> list:
    if uid not in _uid_list:
        return []
    return _uid_list[uid].get("sub_users", [])


def get_dynamic_users(uid: str) -> list:
    if uid not in _uid_list:
        return []
    return _uid_list[uid].get("dynamic_users", [])


def get_record_users(uid: str) -> list:
    if uid not in _uid_list:
        return []
    return _uid_list[uid].get("record_users", [])


def get_sub_info_by_uid(uid: str) -> dict:
    if uid in _uid_list:
        info = _uid_list[uid]
        return {
            "uid": uid,
            "up_name": info["up_name"],
            "room_id": info["room_id"],
        }
    return {}


def get_sub_info_by_roomid(room_id: str) -> dict:
    for uid, info in _uid_list.items():
        if info["room_id"] == room_id:
            return {
                "uid": uid,
                "up_name": info["up_name"],
                "room_id": info["room_id"],
            }
    return {}


def get_sub_info_by_name(up_name: str) -> dict:
    for uid, info in _uid_list.items():
        if info["up_name"] == up_name:
            return {
                "uid": uid,
                "up_name": info["up_name"],
                "room_id": info["room_id"],
            }
    return {}


def update_uid_list(sub_list: Dict[str, Dict[str, dict]]):
    _uid_list.clear()
    for user, user_sub_list in sub_list.items():
        for uid, info in user_sub_list.items():
            if uid not in _uid_list:
                _uid_list[uid] = {
                    "up_name": info["up_name"],
                    "room_id": info["room_id"],
                    "sub_users": [],
                    "record_users": [],
                    "dynamic_users": [],
                }
            _uid_list[uid]["sub_users"].append(user)
            if info.get("record", False):
                _uid_list[uid]["record_users"].append(user)
            if info.get("dynamic", False):
                _uid_list[uid]["dynamic_users"].append(user)
    dump_uid_list()
