import re
from nonebot import on_keyword
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_content

commands = {'是啥', '是什么', '是谁'}
wiki = on_keyword(commands, priority=18)


def split(msg):
    for command in commands:
        if command in msg:
            prefix, suffix = re.split(command, msg)
            return prefix, suffix
    return '', ''


@wiki.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip().strip('.>,?!。，（）()[]【】')
    prefix_words = ['这', '这个', '那', '那个']
    suffix_words = ['意思', '梗', '玩意', '鬼']
    prefix, suffix = split(msg)
    if not prefix or prefix in prefix_words:
        wiki.block = False
        return
    if suffix and suffix not in suffix_words:
        wiki.block = False
        return

    keyword = prefix
    title, content = await get_content(keyword)
    if title:
        wiki.block = True
        await wiki.send(message=title + '：\n----------\n' + content)
        await wiki.finish()
    else:
        wiki.block = False
        return
