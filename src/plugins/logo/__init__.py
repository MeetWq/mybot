import re
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import create_logo

logo = on_command('logo', priority=18)


@logo.handle()
@logo.args_parser
async def _(bot: Bot, event: Event, state: T_State):
    text = event.get_plaintext().strip()
    texts = re.split(r' +', text)
    texts = [t for t in texts if t]
    if len(texts) == 2:
        state['left_text'] = texts[0]
        state['right_text'] = texts[1]


@logo.got('left_text', prompt='请输入文本并用空格分隔，如“Porn hub”')
async def _(bot: Bot, event: Event, state: T_State):
    left_text = state['left_text']
    right_text = state['right_text']
    await logo.send(message='请稍候...')
    file_path = await create_logo(left_text, right_text)
    if file_path:
        await logo.send(message=MessageSegment("image", {"file": "file://" + file_path}))
        await logo.finish()
    else:
        await logo.finish('出错了，请稍后重试')
