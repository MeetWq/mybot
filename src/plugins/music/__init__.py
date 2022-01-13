from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

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


async def handle(matcher: Matcher, source: str, keyword: str):
    msg = await search_song(source, keyword)
    if msg:
        await matcher.finish(msg)
    else:
        await matcher.finish('出错了，请稍后再试')


def create_matchers():

    def create_handler(source: str) -> T_Handler:
        async def handler(msg: Message = CommandArg()):
            keyword = msg.extract_plain_text().strip()
            await handle(matcher, source, keyword)
        return handler

    for source, params in sources.items():
        matcher = on_command(f'{source}music', aliases=params['aliases'],
                             block=True, priority=13)
        matcher.append_handler(create_handler(source))


create_matchers()
