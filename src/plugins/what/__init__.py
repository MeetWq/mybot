import re
from nonebot import on_keyword
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, Message

from .data_source import get_content, download_image

commands = {'是啥', '是什么'}
what = on_keyword(commands, priority=17)


def split(msg):
    for command in commands:
        if command in msg:
            prefix, suffix = re.split(command, msg)
            return prefix, suffix
    return '', ''


@what.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip().strip('.>,?!。，（）()[]【】')
    prefix_words = ['这', '这个', '那', '那个']
    suffix_words = ['意思', '梗', '玩意', '鬼']
    prefix, suffix = split(msg)
    if not prefix or prefix in prefix_words:
        what.block = False
        return
    if suffix and suffix not in suffix_words:
        what.block = False
        return

    keyword = prefix
    title, content, img_urls = await get_content(keyword)
    if title:
        what.block = True
        msgs = [{"type": "text", "data": {"text": title + '：\n----------\n' + content}}]
        for img_url in img_urls:
            img_path = await download_image(img_url)
            if img_path:
                msgs.append({"type": "image", "data": {"file": "file://" + img_path}})
        await what.send(message=Message(msgs))
        await what.finish()
    else:
        what.block = False
        return
