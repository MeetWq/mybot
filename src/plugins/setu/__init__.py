from nonebot import on_keyword, on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_setu


__des__ = '随机涩图'
__cmd__ = '''
@我 setu [keyword]
'''.strip()
__short_cmd__ = __cmd__
__example__ = '''
@小Q setu 伊蕾娜
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


setu = on_keyword({'setu', '涩图', '色图'}, rule=to_me(), priority=14)
setu_ = on_command('setu_', rule=to_me(), permission=SUPERUSER, priority=11)


@setu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    key_word = event.get_plaintext().strip()
    words = ['setu', '涩图', '色图', '来份', '来张',
             '来个', '来点', '发份', '发张', '发个', '发点']
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
