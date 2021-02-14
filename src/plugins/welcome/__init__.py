from nonebot import on_notice
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, GroupIncreaseNoticeEvent

from .data_source import welcome_file_path


async def welcome_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupIncreaseNoticeEvent)


welcome = on_notice(rule=welcome_rule, priority=11)


@welcome.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, GroupIncreaseNoticeEvent):
        await welcome.send(message=MessageSegment("image", {"file": "file://" + welcome_file_path()}))
