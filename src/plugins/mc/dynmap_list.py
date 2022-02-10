import json
import httpx
import traceback
from typing import Dict
from pathlib import Path
from datetime import datetime
from nonebot.log import logger

from .dynmap_source import get_status

data_path = Path("data/mc")
if not data_path.exists():
    data_path.mkdir(parents=True)
dynmap_path = data_path / "dynmap_list.json"


def _load_dynmap_list() -> Dict[str, dict]:
    try:
        return json.load(dynmap_path.open("r", encoding="utf-8"))
    except FileNotFoundError:
        return {}


_dynmap_list = _load_dynmap_list()


def dump_dynmap_list():
    json.dump(
        _dynmap_list,
        dynmap_path.open("w", encoding="utf-8"),
        indent=4,
        separators=(",", ": "),
        ensure_ascii=False,
    )


def get_dynmap_list():
    return _dynmap_list.copy()


def get_dynmap_url(user_id: str) -> str:
    if user_id in _dynmap_list:
        return _dynmap_list[user_id].get("url", "")
    return ""


def get_update_url(user_id: str) -> str:
    if user_id in _dynmap_list:
        return _dynmap_list[user_id].get("update_url", "")
    return ""


def get_poke_status(user_id: str) -> bool:
    if user_id in _dynmap_list:
        return _dynmap_list[user_id].get("poke", False)
    return False


def get_login_status(user_id: str) -> bool:
    if user_id in _dynmap_list:
        return _dynmap_list[user_id].get("username", "") and _dynmap_list[user_id].get(
            "password", ""
        )
    return False


async def fetch_update_url(url: str) -> str:
    url_config = url + "/up/configuration"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url_config)
            result = resp.json()
        world = result["defaultworld"]
        return f"{url}/up/world/{world}"
    except:
        logger.debug(traceback.format_exc())
        return ""


async def bind_dynmap(user_id: str, url: str) -> bool:
    url = url.strip("/#")
    update_url = await fetch_update_url(url)
    if not update_url:
        return False
    status = await get_status(update_url)
    if not status:
        return False
    _dynmap_list[user_id] = {
        "url": url,
        "update_url": update_url,
        "chat": False,
        "poke": False,
        "last_update": int(datetime.now().timestamp() * 1000),
    }
    dump_dynmap_list()
    return True


def unbind_dynmap(user_id: str) -> bool:
    if not get_dynmap_url(user_id):
        return False
    _dynmap_list.pop(user_id)
    dump_dynmap_list()
    return True


def open_chat(user_id: str) -> bool:
    if not get_dynmap_url(user_id):
        return False
    _dynmap_list[user_id]["chat"] = True
    dump_dynmap_list()
    return True


def close_chat(user_id: str) -> bool:
    if not get_dynmap_url(user_id):
        return False
    _dynmap_list[user_id]["chat"] = False
    dump_dynmap_list()
    return True


def open_poke(user_id: str) -> bool:
    if not get_dynmap_url(user_id):
        return False
    _dynmap_list[user_id]["poke"] = True
    dump_dynmap_list()
    return True


def close_poke(user_id: str) -> bool:
    if not get_dynmap_url(user_id):
        return False
    _dynmap_list[user_id]["poke"] = False
    dump_dynmap_list()
    return True


def set_user(user_id: str, username: str, password: str) -> bool:
    if not get_dynmap_url(user_id):
        return False
    _dynmap_list[user_id]["username"] = username
    _dynmap_list[user_id]["password"] = password
    dump_dynmap_list()
    return True


def del_user(user_id: str) -> bool:
    if not get_dynmap_url(user_id):
        return False
    _dynmap_list[user_id].pop("username")
    _dynmap_list[user_id].pop("password")
    dump_dynmap_list()
    return True
