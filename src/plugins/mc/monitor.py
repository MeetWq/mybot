import re
from lxml import etree
from typing import List, Dict
from dataclasses import dataclass, field
from nonebot import get_bot, get_driver
from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_apscheduler import scheduler

from .dynmap_source import get_dynmap_updates
from .dynmap_list import get_dynmap_list

from .config import Config

mc_config = Config.parse_obj(get_driver().config.dict())


@dataclass
class Recorder:
    count: int = 0
    last_time: int = 0
    chats: List[dict] = field(default_factory=list)


chat_recorders: Dict[str, Recorder] = {}


def user_type(user_id: str):
    p_group = r"group_(\d+)"
    p_private = r"private_(\d+)"
    match = re.fullmatch(p_group, user_id)
    if match:
        return "group", match.group(1)
    match = re.fullmatch(p_private, user_id)
    if match:
        return "private", match.group(1)
    return "", user_id


async def send_bot_msg(user_id: str, msg):
    type, id = user_type(user_id)
    bot = get_bot()
    assert isinstance(bot, Bot)
    if type == "group":
        await bot.send_group_msg(group_id=int(id), message=msg)
    elif type == "private":
        await bot.send_private_msg(user_id=int(id), message=msg)


async def update_dynmap():
    dynmap_list = get_dynmap_list()
    for user_id, config in dynmap_list.items():
        if not config["chat"]:
            continue

        url = config["update_url"]
        result = await get_dynmap_updates(url)
        if not result:
            continue

        updates = result["updates"]
        if not updates:
            continue

        if user_id not in chat_recorders:
            chat_recorders[user_id] = Recorder(
                count=1, last_time=updates[-1]["timestamp"]
            )
            continue
        recorder = chat_recorders[user_id]
        recorder.count += 1

        chats = []
        for update in updates:
            if update["type"] == "chat" and update["timestamp"] > recorder.last_time:
                chats.append(update)
        recorder.last_time = updates[-1]["timestamp"]

        if not chats:
            continue
        recorder.chats.extend(chats)


async def dynmap_monitor():
    await update_dynmap()
    for user_id, recorder in chat_recorders.items():
        if recorder.count < 6:
            continue
        else:
            recorder.count = 0
        msgs = []
        for chat in recorder.chats:
            name = chat["playerName"]
            name = etree.HTML(name, etree.HTMLParser()).xpath("string(.)").strip()
            message = chat["message"]
            msgs.append(f"[dynmap] {name}: {message}")
        recorder.chats = []
        if msgs:
            msg = "\n".join(msgs)
            await send_bot_msg(user_id, msg)


dynmap_cron = mc_config.dynmap_cron
scheduler.add_job(
    dynmap_monitor,
    "cron",
    second=dynmap_cron[0],
    minute=dynmap_cron[1],
    hour=dynmap_cron[2],
    day=dynmap_cron[3],
    month=dynmap_cron[4],
    year=dynmap_cron[5],
    id="dynmap_monitor",
    coalesce=True,
)
