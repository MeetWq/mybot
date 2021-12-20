import re
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, Message

from .data_source import get_pixiv, search_by_image


__des__ = 'Pixiv图片、以图搜图'
__cmd__ = '''
1. pixiv {日榜/周榜/月榜/id/关键词}，关键词搜索需要 @我
2. 搜图 {图片/url}
'''.strip()
__example__ = '''
pixiv 日榜
@小Q pixiv 伊蕾娜
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


pixiv = on_command('pixiv', priority=12)


@pixiv.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = event.get_plaintext().strip()
    if not keyword:
        await pixiv.finish()

    if not keyword.isdigit() and keyword not in ['日榜', 'day', '周榜', 'week', '月榜', 'month', '月榜', 'month']:
        if not event.is_tome():
            await pixiv.finish()

    msg = await get_pixiv(keyword)
    if not str(msg):
        await pixiv.finish('出错了，请稍后再试')
    await pixiv.finish(msg)


pic_search = on_command('搜图', priority=25)


@pic_search.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.get_message()
    if msg:
        state['img_url'] = msg


@pic_search.got('img_url', prompt='请发送一张图片或图片链接')
async def _(bot: Bot, event: Event, state: T_State):
    img_url = parse_url(state['img_url'])
    if not img_url:
        await pic_search.reject()
    msg = await search_by_image(img_url)
    if not msg:
        await pic_search.finish('出错了，请稍后再试')
    await pic_search.finish(msg)


def parse_url(msg):
    img_url = ''
    if isinstance(msg, Message):
        for msg_seg in msg:
            if msg_seg.type == 'image':
                img_url = msg_seg.data['url']
            elif msg_seg.type == 'text':
                text = msg_seg.data['text']
                if text.startswith('http'):
                    img_url = text.split(' ')[0]
    elif isinstance(msg, str):
        if msg.startswith('http'):
            img_url = msg.split(' ')[0]
        else:
            match = re.search(r'\[CQ:image.*?url=(.*?)\]', msg)
            if match:
                img_url = match.group(1)
    return img_url
