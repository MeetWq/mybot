from nonebot import export, on_command, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_voice

export = export()
export.description = '语音合成'
export.usage = 'Usage:\n  1. speak [options] {words}\n  2. @我，说{words}'
export.options = 'Options:\n  -t, --type 语音类型，目前支持女声(0)和男声(1)'
export.notice = 'Notice:\n  支持中文和日文'
export.help = export.description + '\n' + export.usage + '\n' + export.options + '\n' + export.notice

speak_parser = ArgumentParser()
speak_parser.add_argument('-t', '--type', type=int, default=0)
speak_parser.add_argument('words', nargs='+')

speak = on_shell_command('speak', parser=speak_parser, priority=14)
speak_at = on_command('说', rule=to_me(), priority=26)


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

    await speak.send(message='请稍候...')
    file_path = await get_voice(words, type)
    if file_path:
        await speak.send(message=MessageSegment.record(file='file://' + file_path))
    else:
        await speak.send(message='出错了，请稍后重试')


@speak_at.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    if not msg:
        await speak_at.send(message=export.usage)
        return

    await speak_at.send(message='请稍候...')
    file_path = await get_voice(msg)
    if file_path:
        await speak_at.send(message=MessageSegment.record(file='file://' + file_path))
    else:
        await speak_at.send(message='出错了，请稍后重试')
