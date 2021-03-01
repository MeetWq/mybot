import os

from nonebot import get_driver, on_command, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_reply

nhd_girl = on_regex(r'^[Nn][Hh][Dd]娘', priority=13)


@nhd_girl.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip().lower().replace('nhd娘', '')
    reply = get_reply(msg, event)
    if reply:
        await nhd_girl.send(message=reply)
        await nhd_girl.finish()
