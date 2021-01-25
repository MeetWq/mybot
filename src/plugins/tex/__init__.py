import os
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import tex2pic

dir_path = os.path.split(os.path.realpath(__file__))[0]

tex = on_command('tex', aliases={'latex', 'TeX', 'LaTeX'}, rule=to_me(), priority=14)


@tex.handle()
async def _(bot: Bot, event: Event, state: T_State):
    equation = str(event.get_message()).strip()
    if equation:
        state['equation'] = equation


@tex.got('equation', prompt='请输入LaTeX公式')
async def _(bot: Bot, event: Event, state: T_State):
    equation = state['equation'].strip().strip('$')
    file_path = os.path.join(dir_path, 'tex.png')
    await tex.send(message='请稍候...')
    if tex2pic(equation, file_path):
        await tex.send(message=MessageSegment("image", {"file": "file://" + file_path}))
        await tex.finish()
    else:
        await tex.finish('出错了，请检查公式或稍后重试')
