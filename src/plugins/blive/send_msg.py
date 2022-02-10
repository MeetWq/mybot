import re
from typing import Union
import nonebot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message

from .uid_list import get_sub_users, get_dynamic_users, get_record_users


async def send_live_msg(uid: str, msg: Union[str, Message]):
    users = get_sub_users(uid)
    for user_id in users:
        await send_bot_msg(user_id, msg)


async def send_dynamic_msg(uid: str, msg: Union[str, Message]):
    users = get_dynamic_users(uid)
    for user_id in users:
        await send_bot_msg(user_id, msg)


async def send_record_msg(uid: str, msg: Union[str, Message]):
    users = get_record_users(uid)
    for user_id in users:
        await send_bot_msg(user_id, msg)


async def send_bot_msg(user_id: str, msg: Union[str, Message]):
    type, id = user_type(user_id)
    try:
        bot = nonebot.get_bot()
        assert isinstance(bot, Bot)
        if type == "group":
            await bot.send_group_msg(group_id=int(id), message=msg)
        elif type == "private":
            await bot.send_private_msg(user_id=int(id), message=msg)
    except:
        logger.warning(f"send msg failed, user_id: {user_id}, msg: {msg}")


async def send_superuser_msg(msg: Union[str, Message]):
    try:
        bot = nonebot.get_bot()
        assert isinstance(bot, Bot)
        user_id = list(bot.config.superusers)[0]
        await bot.send_private_msg(user_id=int(user_id), message=msg)
    except:
        logger.warning(f"send superuser msg failed, msg: {msg}")


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
