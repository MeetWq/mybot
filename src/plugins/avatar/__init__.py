import re
from typing import Type
from nonebot import export, on_startswith
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_image

export = export()
export.description = '头像相关表情生成'
export.usage = 'Usage:\n  摸/撕/丢/爬/精神支柱 {qq/@user/自己}'
export.help = export.description + '\n' + export.usage

petpet = on_startswith('摸', priority=26)
tear = on_startswith('撕', priority=26)
throw = on_startswith('丢', priority=26)
crawl = on_startswith('爬', priority=26)
support = on_startswith('精神支柱', priority=26)


async def handle(matcher: Type[Matcher], event: Event, command: str, type: str):
    msg = event.get_message()
    msg_text = event.get_plaintext().strip()
    qq = ''
    for msg_seg in msg:
        if msg_seg.type == 'at':
            qq = msg_seg.data['qq']
            break
    if not qq:
        msg_content = re.sub(command, '', msg_text).strip()
        if msg_content.isdigit():
            qq = msg_content
        elif msg_content == '自己':
            qq = event.user_id
    if qq:
        matcher.block = True
        image = await get_image(qq, type)
        if image:
            await matcher.send(message=image)
            await matcher.finish()
        else:
            await matcher.finish(message='出错了，请稍后再试')
    matcher.block = False
    await matcher.finish()



@petpet.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(petpet, event, '摸', 'petpet')


@tear.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(tear, event, '撕', 'tear')


@throw.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(throw, event, '丢', 'throw')


@crawl.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(crawl, event, '爬', 'crawl')


@support.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(support, event, '精神支柱', 'support')
