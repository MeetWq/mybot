from nonebot import get_driver, on_regex, on_message
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, GroupMessageEvent

from .data_source import get_reply
from .config import Config

global_config = get_driver().config
nhd_config = Config(**global_config.dict())


async def nhd_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return str(event.get_user_id()) in global_config.superusers or \
        (isinstance(event, GroupMessageEvent) and str(event.group_id) in nhd_config.nhd_group)


async def nhd_rule_at(bot: Bot, event: Event, state: T_State) -> bool:
    return event.is_tome() and isinstance(event, GroupMessageEvent) and str(event.group_id) in nhd_config.nhd_group


nhd_girl = on_regex(r'^[Nn][Hh][Dd]娘', rule=nhd_rule, priority=13)
nhd_girl_at = on_message(rule=nhd_rule_at, priority=14)


@nhd_girl.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip().lower().replace('nhd娘', '')
    reply = await get_reply(msg, event)
    if reply:
        await nhd_girl.send(message=reply)
        await nhd_girl.finish()


@nhd_girl_at.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip().lower()
    reply = await get_reply(msg, event)
    if reply:
        nhd_girl_at.block = True
        await nhd_girl_at.send(message=reply)
        await nhd_girl_at.finish()
    else:
        nhd_girl_at.block = False
