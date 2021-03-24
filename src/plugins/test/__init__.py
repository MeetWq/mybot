from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

test = on_command('test', rule=to_me(), permission=SUPERUSER, priority=20)


@test.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await test.send(message='hello')
