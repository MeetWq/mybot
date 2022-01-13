from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment

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


speak = on_command('speak', aliases={'说'},
                   block=True, rule=to_me(), priority=11)


@speak.handle()
async def _(msg: Message = CommandArg()):
    msg = msg.extract_plain_text().strip()
    if not msg:
        await speak.finish()

    voice = await get_voice(msg)
    if voice:
        await speak.finish(MessageSegment.record(voice))
    else:
        await speak.finish('出错了，请稍后再试')
