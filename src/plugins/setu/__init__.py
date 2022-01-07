from nonebot import on_command
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


setu = on_command('setu', aliases={'涩图', '色图'}, rule=to_me(), priority=14)
r18 = on_command('r18', rule=to_me(), permission=SUPERUSER, priority=14)


@setu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = event.get_plaintext().strip()
    img = await get_setu(keyword=keyword)
    if not img:
        await setu.finish('出错了，请稍后再试')
    await setu.finish(message=img)


@r18.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = event.get_plaintext().strip()
    img = await get_setu(keyword=keyword, r18=True)
    if not img:
        await r18.finish('出错了，请稍后再试')
    await r18.finish(message=img)
