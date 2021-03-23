import os
from nonebot import on_notice
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, GroupIncreaseNoticeEvent

dir_path = os.path.split(os.path.realpath(__file__))[0]
welcome_path = os.path.join(dir_path, 'welcome.jpg')

async def welcome_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupIncreaseNoticeEvent)


welcome = on_notice(rule=welcome_rule, priority=12)


@welcome.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, GroupIncreaseNoticeEvent):
        await welcome.send(message=MessageSegment.image(file='file://' + welcome_path))
