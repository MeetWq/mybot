from typing import Type
from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_image

export = export()
export.description = '头像相关表情生成'
export.usage = 'Usage:\n  摸/撕/丢/爬/亲/贴/顶/精神支柱 {qq/@user/自己/图片}'
export.help = export.description + '\n' + export.usage

petpet = on_command('摸', aliases={'rua', '摸摸'}, priority=26)
tear = on_command('撕', priority=26)
throw = on_command('丢', priority=26)
crawl = on_command('爬', priority=26)
kiss = on_command('亲', aliases={'亲亲'}, priority=26)
kiss_me = on_command('亲我', priority=25)
rub = on_command('贴', aliases={'贴贴'}, priority=26)
rub_me = on_command('贴我', priority=25)
duang = on_command('顶', priority=26)
support = on_command('精神支柱', priority=26)


async def handle(matcher: Type[Matcher], event: Event, type: str, reverse: bool = False):
    msg = event.get_message()
    msg_text = event.get_plaintext().strip()
    self_id = event.user_id
    user_id = ''

    for msg_seg in msg:
        if msg_seg.type == 'at':
            user_id = msg_seg.data['qq']
            break

    if not user_id:
        if msg_text.isdigit():
            user_id = msg_text
        elif msg_text == '自己':
            user_id = event.user_id

    img_url = ''
    if not user_id:
        for msg_seg in msg:
            if msg_seg.type == 'image':
                img_url = msg_seg.data['url']
                break

    image = None
    if user_id:
        image = await get_image(type, self_id, user_id=user_id, reverse=reverse)
    elif img_url:
        image = await get_image(type, self_id, img_url=img_url, reverse=reverse)
    else:
        matcher.block = False
        await matcher.finish()

    matcher.block = True
    if image:
        await matcher.send(message=image)
        await matcher.finish()
    else:
        await matcher.finish(message='出错了，请稍后再试')


@petpet.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(petpet, event, 'petpet')


@tear.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(tear, event, 'tear')


@throw.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(throw, event, 'throw')


@crawl.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(crawl, event, 'crawl')


@kiss.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(kiss, event, 'kiss')


@kiss_me.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(kiss, event, 'kiss', reverse=True)


@rub.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(rub, event, 'rub')


@rub_me.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(rub, event, 'rub', reverse=True)


@duang.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(duang, event, 'duang')


@support.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await handle(support, event, 'support')
