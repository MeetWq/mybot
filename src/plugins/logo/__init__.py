from nonebot import export, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import create_logo

export = export()
export.description = 'logo生成'
export.usage = 'Usage:\n  logo [-s style] {text}'
export.options = 'Options:\n  -s, --style logo风格，目前支持：pornhub(默认)、youtube、5000choyen、douyin'
export.example = 'Example: \n  logo -s youtube text1 text2'
export.example1 = 'Example: \n  logo -s youtube "te xt1" text2'
export.notice = 'Notice:\n  pornhub, youtube和5000choyen需输入2段文字并用空格分开'
export.help = export.description + '\n' + export.usage + '\n' + export.options + '\n' + export.example + '\n' + export.notice

logo_parser = ArgumentParser()
logo_parser.add_argument('-s', '--style', default='pornhub')
logo_parser.add_argument('text', nargs='+')

logo = on_shell_command('logo', parser=logo_parser, priority=16)


@logo.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'text'):
        await logo.finish()

    style = args.style
    if style not in ['pornhub', 'youtube', '5000choyen', 'douyin']:
        await logo.finish(export.options)

    texts = args.text
    if style in ['pornhub', 'youtube', '5000choyen'] and len(texts) != 2:
        if len(texts) < 2:
            await logo.finish('参数数量不符\n' + export.notice + '\n' + export.example)
        else:
            await logo.finish('参数数量不符\n' + export.notice + '，带空格的参数需加引号' + '\n' + export.example1)

    image = await create_logo(texts, style)
    if image:
        await logo.finish(image)
    else:
        await logo.finish('出错了，请稍后再试')
