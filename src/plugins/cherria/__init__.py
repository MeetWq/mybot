import os

from nonebot import on_command, on_endswith
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_image, get_record, get_words

get_jpg = on_endswith('.jpg', priority=11)
get_mp3 = on_endswith('.mp3', priority=11)
cherry_words = on_command('cherry words', aliases={'樱桃语录', '樱语'}, priority=12)


@get_jpg.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    keyword = os.path.splitext(keyword)[0]
    img_path = get_image(keyword)
    if img_path:
        get_jpg.block = True
        await get_jpg.send(message=MessageSegment("image", {"file": "file://" + img_path}))
        await get_jpg.finish()
    else:
        get_jpg.block = False


@get_mp3.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    keyword = os.path.splitext(keyword)[0]
    record_path = get_record(keyword)
    if record_path:
        get_mp3.block = True
        await get_mp3.send(message=MessageSegment("record", {"file": "file://" + record_path}))
        await get_mp3.finish()
    else:
        get_mp3.block = False


@cherry_words.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    img_path = get_words(keyword)
    if img_path:
        await cherry_words.send(message=MessageSegment("image", {"file": "file://" + img_path}))
        await cherry_words.finish()
