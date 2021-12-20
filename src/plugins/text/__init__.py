from typing import Type
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler, T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_text, commands


__des__ = '抽象话等多种文本生成'
__cmd__ = '''
抽象话/火星文/蚂蚁文/翻转文字/故障文字 {text}
'''.strip()
__short_cmd__ = '抽象话、火星文 等'
__example__ = '''
抽象话 那真的牛逼
火星文 那真的牛逼
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


async def handle(matcher: Type[Matcher], event: Event, type: str):
    text = event.get_plaintext().strip()
    msg = await get_text(text, type)
    if msg:
        await matcher.finish(msg)
    else:
        await matcher.finish('出错了，请稍后再试')


def create_matchers():

    def create_handler(type: str) -> T_Handler:
        async def handler(bot: Bot, event: Event, state: T_State):
            await handle(matcher, event, type)
        return handler

    for type, params in commands.items():
        matcher = on_command(
            f'text {type}', aliases=params['aliases'], priority=13)
        matcher.append_handler(create_handler(type))


create_matchers()
