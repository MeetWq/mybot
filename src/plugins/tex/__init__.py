from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, unescape, Event, MessageSegment

from .data_source import tex2pic

tex = on_command('tex', aliases={'latex', 'TeX', 'LaTeX'}, rule=to_me(), priority=14)


@tex.handle()
@tex.args_parser
async def _(bot: Bot, event: Event, state: T_State):
    equation = unescape(event.get_plaintext().strip().strip('$'))
    if equation:
        state['equation'] = equation


@tex.got('equation', prompt='请输入LaTeX公式')
async def _(bot: Bot, event: Event, state: T_State):
    equation = state['equation']
    await tex.send(message='请稍候...')
    file_path = tex2pic(equation)
    if file_path:
        await tex.send(message=MessageSegment("image", {"file": "file://" + file_path}))
        await tex.finish()
    else:
        await tex.finish('出错了，请检查公式或稍后重试')
