from nonebot import export, on_command, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_voice

export = export()
export.description = '语音合成'
export.usage = 'Usage:\n  1. speak [options] {words}\n  2. @我，说{words}'
export.options = 'Options:\n  -t, --type 语音类型，目前支持女声(0)和男声(1)'
export.notice = 'Notice:\n  支持中文和日文，但不支持混合'
export.help = export.description + '\n' + export.usage + '\n' + export.options + '\n' + export.notice

speak_parser = ArgumentParser()
speak_parser.add_argument('-t', '--type', type=int, default=0)
speak_parser.add_argument('words', nargs='+')

speak = on_shell_command('speak', parser=speak_parser, priority=18)
speak_at = on_command('说', rule=to_me(), priority=18)


@speak.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'words'):
        await speak.finish(export.usage)

    words = args.words
    words = ' '.join(words)
    if not words:
        await speak.finish(export.usage)

    type = args.type
    if type not in [0, 1]:
        await speak.finish(export.options)

    voice = await get_voice(words, type)
    if voice:
        await speak.finish(voice)
    else:
        await speak.finish('出错了，请稍后再试')


@speak_at.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.get_plaintext().strip()
    if not msg:
        await speak_at.finish()

    voice = await get_voice(msg)
    if voice:
        await speak_at.finish(voice)
    else:
        await speak_at.finish('出错了，请稍后再试')
