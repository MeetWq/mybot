from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_voice

__des__ = '文字转语音'
__cmd__ = '''
@我 说 {text}
'''.strip()
__short_cmd__ = __cmd__
__example__ = '''
@小Q 说你是猪
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


speak = on_command('说', rule=to_me(), priority=18)


@speak.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.get_plaintext().strip()
    if not msg:
        await speak.finish()

    voice = await get_voice(msg)
    if voice:
        await speak.finish(voice)
    else:
        await speak.finish('出错了，请稍后再试')
