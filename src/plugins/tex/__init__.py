import re
from nonebot import export, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, unescape, Event, MessageSegment
from nonebot.log import logger

from .data_source import tex2pic

export = export()
export.description = 'LaTeX公式'
export.usage = 'Usage:\n  tex [options] {equation}'
export.options = 'Options:\n  -b, --border 图片白边的宽度，默认为2\n  -r --resolution 图片分辨率，默认为1000'
export.notice = 'Notice:\n  支持行内公式和少量行间公式'
export.help = export.description + '\n' + export.usage + '\n' + export.options + '\n' + export.notice

tex_parser = ArgumentParser()
tex_parser.add_argument('-b', '--border', type=int, default=2)
tex_parser.add_argument('-r', '--resolution', type=int, default=1000)
tex_parser.add_argument('equation', nargs='+')

tex = on_shell_command('tex', parser=tex_parser, priority=15)


@tex.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'equation'):
        await tex.finish(export.usage)

    equation = unescape(event.get_plaintext()).strip()
    equation = re.sub(r'-b +.*? +(.*?)', lambda x: x.group(1), equation)
    equation = re.sub(r'--border +.*? +(.*?)', lambda x: x.group(1), equation)
    equation = re.sub(r'-r +.*? +(.*?)', lambda x: x.group(1), equation)
    equation = re.sub(r'--resolution +.*? +(.*?)', lambda x: x.group(1), equation)
    equation = equation.strip().strip('"').strip('$')
    logger.debug(equation)
    if not equation:
        await tex.finish(export.usage)

    await tex.send(message='请稍候...')
    file_path = await tex2pic(equation, border=args.border, resolution=args.resolution)
    if file_path:
        await tex.send(message=MessageSegment.image(file='file://' + file_path))
        await tex.finish()
    else:
        await tex.finish('出错了，请检查公式或稍后再试')
