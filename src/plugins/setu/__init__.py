from nonebot import export, on_keyword, on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_pic_url

export = export()
export.description = '随机涩图'
export.usage = 'Usage:\n  setu/涩图 [keyword]'
export.notice = 'Notice:\n  需要@我'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

setu = on_keyword({'setu', '涩图', '色图'}, rule=to_me(), priority=24)
setu_ = on_command('setu_', rule=to_me(), permission=SUPERUSER, priority=23)


@setu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    key_word = str(event.get_message()).strip()
    words = ['setu', '涩图', '色图', '来份', '来张', '来个', '来点', '发份', '发张', '发个', '发点']
    for word in words:
        key_word = key_word.replace(word, '')
    await setu.send('请稍候...')
    img_url = await get_pic_url(key_word=key_word)
    if not img_url:
        await setu.finish('找不到相关的涩图')
    await setu.send(message=MessageSegment.image(file=img_url))
    await setu.finish()


@setu_.handle()
async def _(bot: Bot, event: Event, state: T_State):
    key_word = str(event.get_message()).replace('setu_', '').strip()
    await setu_.send('请稍候...')
    img_url = await get_pic_url(key_word=key_word, r18=True)
    if not img_url:
        await setu_.finish('找不到相关的涩图')
    await setu_.send(message=MessageSegment.image(file=img_url))
    await setu_.finish()
