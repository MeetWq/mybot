from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import check_text


asoulcnki = on_command('asoulcnki', aliases={'枝网查重', '查重 ', '查重\n', '查重\r\n'}, priority=39)


@asoulcnki.handle()
async def _(bot: Bot, event: Event, state: T_State):
    text = event.get_plaintext().strip()
    if not text:
        await asoulcnki.finish()

    if len(text) >= 1000:
        await asoulcnki.finish('文本过长，长度须在10-1000之间')
    elif len(text) <= 10:
        await asoulcnki.finish('文本过短，长度须在10-1000之间')

    msg = await check_text(text)
    if msg:
        await asoulcnki.finish(msg)
    else:
        await asoulcnki.finish('出错了，请稍后再试')
