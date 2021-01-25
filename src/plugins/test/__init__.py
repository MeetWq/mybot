from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, Message, MessageSegment
from nonebot.permission import SUPERUSER

test = on_command('test', permission=SUPERUSER, rule=to_me(), priority=19)


@test.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await test.send(message='hello')
