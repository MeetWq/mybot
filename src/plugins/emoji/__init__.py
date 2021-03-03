import os

from nonebot import on_regex, on_endswith
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_emoji_path, get_image, download_image

ac = on_regex(r'^ac\d{2,4}$', priority=11)
em = on_regex(r'^em\d{2}$', priority=11)
em_nhd = on_regex(r'^emm\d{1,3}$', priority=11)
mahjong = on_regex(r'^[acf]:?\d{3}$', priority=11)
ms = on_regex(r'^ms\d{2}$', priority=11)
tb = on_regex(r'^tb\d{2}$', priority=11)
cc98 = on_regex(r'^[Cc][Cc]98\d{2}$', priority=11)

get_jpg = on_endswith('.jpg', priority=12)


@ac.handle()
@em.handle()
@em_nhd.handle()
@mahjong.handle()
@ms.handle()
@tb.handle()
@cc98.handle()
async def _(bot: Bot, event: Event, state: T_State):
    file_name = str(event.get_message()).strip()
    file_path = get_emoji_path(file_name)
    if file_path:
        await bot.send(event=event, message=MessageSegment("image", {"file": "file://" + file_path}))
    else:
        await bot.send(event=event, message="找不到该表情")


@get_jpg.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    keyword = os.path.splitext(keyword)[0]
    img_url = await get_image(keyword)
    if not img_url:
        await get_jpg.finish(message="找不到相关的图片")
    img_path = await download_image(img_url)
    if not img_path:
        await get_jpg.finish("下载出错，请稍后再试")
    await get_jpg.send(message=MessageSegment("image", {"file": "file://" + img_path}))
    await get_jpg.finish()
