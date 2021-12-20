import shlex
from typing import Type
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler, T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import create_logo, commands


__des__ = 'pornhub等风格logo生成'
__cmd__ = '''
pornhub：ph {text1} {text2}
youtube：yt {text1} {text2}
5000兆円欲しい!：5000兆 {text1} {text2}
抖音：douyin {text}
'''.strip()
__short_cmd__ = 'ph、yt、5000兆、douyin'
__example__ = '''
ph Porn Hub
yt You Tube
5000兆 我去 初音未来
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


async def handle(matcher: Type[Matcher], event: Event, style: str):
    text = event.get_plaintext().strip()
    if not text:
        await matcher.finish()

    arg_num = commands[style]['arg_num']
    texts = [text] if arg_num == 1 else shlex.split(text)
    if len(texts) != arg_num:
        await matcher.finish('参数数量不符')

    image = await create_logo(texts, style)
    if image:
        await matcher.finish(MessageSegment.image(image))
    else:
        await matcher.finish('出错了，请稍后再试')


def create_matchers():

    def create_handler(style: str) -> T_Handler:
        async def handler(bot: Bot, event: Event, state: T_State):
            await handle(matcher, event, style)
        return handler

    for style, params in commands.items():
        matcher = on_command(
            style, aliases=params['aliases'], priority=13)
        matcher.append_handler(create_handler(style))


create_matchers()
