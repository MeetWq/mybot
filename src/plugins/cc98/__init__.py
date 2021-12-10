from typing import Type
from nonebot import on_regex
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler, T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, unescape

from .emoji import emoji_list, get_emoji


async def handle_emoji(matcher: Type[Matcher], event: Event, dir_name: str):
    file_name = unescape(event.get_plaintext()).strip().strip('[').strip(']')
    img = get_emoji(dir_name, file_name)
    if img:
        await matcher.send(MessageSegment.image(img))
    else:
        await matcher.send('找不到该表情')


def create_emoji_matchers():

    def create_handler(dir_name: str) -> T_Handler:
        async def handler(bot: Bot, event: Event, state: T_State):
            await handle_emoji(matcher, event, dir_name)
        return handler

    for _, params in emoji_list.items():
        matcher = on_regex(params['pattern'], priority=14)
        matcher.append_handler(create_handler(params['dir_name']))


create_emoji_matchers()
