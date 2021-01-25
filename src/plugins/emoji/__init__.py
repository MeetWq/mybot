from nonebot import on_regex, on_keyword
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_emoji_path, get_random_pic

ac = on_regex(r'^ac\d{2,4}', rule=to_me(), priority=15)
em = on_regex(r'^em\d{2}', rule=to_me(), priority=15)
mahjong = on_regex(r'^[acf]:?\d{3}', rule=to_me(), priority=15)
ms = on_regex(r'^ms\d{2}', rule=to_me(), priority=15)
tb = on_regex(r'^tb\d{2}', rule=to_me(), priority=15)
cherry = on_keyword({'樱桃', '嗯桃', '林雪樱'}, rule=to_me(), priority=15)
rabbit = on_keyword({'兔兔', '小夏', '夏珺'}, rule=to_me(), priority=15)
ria = on_keyword({'ria', 'Ria', '璃亚'}, rule=to_me(), priority=15)


@ac.handle()
@em.handle()
@mahjong.handle()
@ms.handle()
@tb.handle()
async def _(bot: Bot, event: Event, state: T_State):
    file_name = str(event.get_message()).strip()
    file_path = get_emoji_path(file_name)
    if file_path:
        await ac.send(message=MessageSegment("image", {"file": "file://" + file_path}))
        await ac.finish()
    await ac.finish(message="找不到该表情")


@cherry.handle()
async def _(bot: Bot, event: Event, state: T_State):
    file_path = get_random_pic(name='cherry')
    if file_path:
        await ac.send(message=MessageSegment("image", {"file": "file://" + file_path}))
        await ac.finish()


@rabbit.handle()
async def _(bot: Bot, event: Event, state: T_State):
    file_path = get_random_pic(name='rabbit')
    if file_path:
        await ac.send(message=MessageSegment("image", {"file": "file://" + file_path}))
        await ac.finish()


@ria.handle()
async def _(bot: Bot, event: Event, state: T_State):
    file_path = get_random_pic(name='ria')
    if file_path:
        await ac.send(message=MessageSegment("image", {"file": "file://" + file_path}))
        await ac.finish()
