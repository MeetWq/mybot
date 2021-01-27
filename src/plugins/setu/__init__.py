import os
from nonebot import on_keyword
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_pic_url, download_image

dir_path = os.path.split(os.path.realpath(__file__))[0]

setu = on_keyword({'setu', '涩图', '色图'}, rule=to_me(), priority=16)


@setu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    key_word = msg
    words = ['setu', '涩图', '色图', '来份', '来张', '来个', '来点', '发份', '发张', '发个', '发点']
    for word in words:
        key_word = key_word.replace(word, '')
    await setu.send('请稍候...')
    img_url = await get_pic_url(key_word=key_word)
    if not img_url:
        await setu.finish('找不到相关的涩图')
    img_path = os.path.join(dir_path, 'images', os.path.basename(img_url))
    if not await download_image(img_url, img_path):
        await setu.finish('下载出错，请稍后再试')
    await setu.send(message=MessageSegment("image", {"file": "file://" + img_path}))
    await setu.finish()

