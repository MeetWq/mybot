from nonebot import export, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import create_logo

export = export()
export.description = 'logo生成'
export.usage = 'Usage:\n  logo [options] {text}'
export.options = 'Options:\n  -s, --style logo风格，目前支持：pornhub(默认)、youtube、5000兆(5000choyen)、抖音(douyin)、cocacola、harrypotter'
export.notice = 'Notice:\n  pornhub, youtube和5000choyen需输入2段文字并用空格分开'
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
    if style not in ['pornhub', 'youtube', '5000choyen', 'douyin', 'cocacola', 'harrypotter']:
        await logo.finish(export.options)

    texts = args.text
    if style in ['pornhub', 'youtube', '5000choyen'] and len(texts) != 2:
        await logo.finish('参数数量不符\n' + export.usage + '\n' + export.notice)

    image = await create_logo(texts, style)
    if image:
        await logo.finish(image)
    else:
        await logo.finish('出错了，请稍后再试')
