from nonebot import export, on_keyword, on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_setu

export = export()
export.description = '随机涩图'
export.usage = 'Usage:\n  setu/涩图 [keyword]'
export.notice = 'Notice:\n  需要@我'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

setu = on_keyword({'setu', '涩图', '色图'}, rule=to_me(), priority=24)
setu_ = on_command('setu_', rule=to_me(), permission=SUPERUSER, priority=23)


@setu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    key_word = event.get_plaintext().strip()
    words = ['setu', '涩图', '色图', '来份', '来张', '来个', '来点', '发份', '发张', '发个', '发点']
    for word in words:
        key_word = key_word.replace(word, '')
    img = await get_setu(key_word=key_word)
    if not img:
        await setu.finish('出错了，请稍后再试')
    await setu.finish(message=img)


@setu_.handle()
async def _(bot: Bot, event: Event, state: T_State):
    key_word = event.get_plaintext().strip()
    img = await get_setu(key_word=key_word, r18=True)
    if not img:
        await setu_.finish('出错了，请稍后再试')
    await setu_.finish(message=img)
