from typing import Type
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler, T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import search_song, sources


__des__ = '点歌'
__cmd__ = '''
点歌/qq点歌/网易点歌/酷狗点歌/咪咕点歌/b站点歌 {keyword}
默认为qq点歌
'''.strip()
__short_cmd__ = '点歌 {keyword}'
__example__ = '''
点歌 勾指起誓
b站点歌 勾指起誓
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


async def handle(matcher: Type[Matcher], event: Event, source: str):
    keyword = event.get_plaintext().strip()
    msg = await search_song(keyword, source)
    if msg:
        await matcher.finish(msg)
    else:
        await matcher.finish('出错了，请稍后再试')


def create_matchers():

    def create_handler(source: str) -> T_Handler:
        async def handler(bot: Bot, event: Event, state: T_State):
            await handle(matcher, event, source)
        return handler

    for source, params in sources.items():
        matcher = on_command(
            f'music {source}', aliases=params['aliases'], priority=13)
        matcher.append_handler(create_handler(source))


create_matchers()
