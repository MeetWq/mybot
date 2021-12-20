import os
import shlex
from typing import Type
from nonebot.matcher import Matcher
from nonebot import on_endswith, on_command
from nonebot.typing import T_Handler, T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_random_emoji, make_emoji, emojis


__des__ = '表情包制作、随机表情包'
emojis_help = [f"{'/'.join(list(e['aliases']))}" +
               (f"，需要输入{e['arg_num']}段文字" if e['arg_num'] > 1 else ' xxx')
               for e in emojis.values()]
emojis_help = '\n'.join(emojis_help)
__cmd__ = f'''
1、{{keyword}}.jpg，随机表情包
2、表情包制作，目前支持：
{emojis_help}
'''.strip()
__example__ = '''
真香.jpg
王境泽 我就是饿死 死外边 不会吃你们一点东西 真香
鲁迅说 我没说过这句话
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


end_jpg = on_endswith('.jpg', priority=14)


@end_jpg.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msgs = event.get_message()
    if len(msgs) > 1:
        return
    keyword = str(msgs).strip()
    keyword = os.path.splitext(keyword)[0]
    if len(keyword) > 20:
        return
    img_url = await get_random_emoji(keyword)
    if not img_url:
        await end_jpg.finish('找不到相关的图片')
    await end_jpg.finish(MessageSegment.image(img_url))


async def handle(matcher: Type[Matcher], event: Event, type: str):
    text = event.get_plaintext().strip()
    if not text:
        await matcher.finish()

    arg_num = emojis[type]['arg_num']
    texts = [text] if arg_num == 1 else shlex.split(text)
    if len(texts) < arg_num:
        await matcher.finish(f'该表情包需要输入{arg_num}段文字')
    elif len(texts) > arg_num:
        await matcher.finish(f'参数数量不符，若包含空格请加引号')

    msg = await make_emoji(type, texts)
    if msg:
        await matcher.finish(msg)
    else:
        await matcher.finish('出错了，请稍后再试')


def create_matchers():

    def create_handler(style: str) -> T_Handler:
        async def handler(bot: Bot, event: Event, state: T_State):
            await handle(matcher, event, style)
        return handler

    for type, params in emojis.items():
        matcher = on_command(
            type, aliases=params['aliases'], priority=13)
        matcher.append_handler(create_handler(type))


create_matchers()
