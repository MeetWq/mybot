import re
from nonebot import export, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import create_logo

export = export()
export.description = 'logo生成'
export.usage = 'Usage:\n  logo [options] {text}'
export.options = 'Options:\n  -s, --style logo风格，目前支持：pornhub(默认)、youtube、抖音(douyin)、cocacola、harrypotter'
export.notice = 'Notice:\n  pornhub和youtube需输入2段文字并用空格分开'
export.help = export.description + '\n' + export.usage + '\n' + export.options + '\n' + export.notice

logo_parser = ArgumentParser()
logo_parser.add_argument('-s', '--style', default='pornhub')
logo_parser.add_argument('text', nargs='+')

logo = on_shell_command('logo', parser=logo_parser, priority=16)


@logo.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'text'):
        await logo.finish(export.usage)

    style = args.style
    if style not in ['pornhub', 'youtube', 'douyin', 'cocacola', 'harrypotter']:
        await logo.finish(export.options)

    texts = args.text
    if style in ['pornhub', 'youtube'] and len(texts) != 2:
        await logo.finish('参数数量不符\n' + export.usage + '\n' + export.notice)

    await logo.send(message='请稍候...')
    file_path = await create_logo(texts, style)
    if file_path:
        await logo.send(message=MessageSegment.image(file='file://' + file_path))
        await logo.finish()
    else:
        await logo.finish('出错了，请稍后再试')
