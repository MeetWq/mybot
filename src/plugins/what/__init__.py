import re
from nonebot import on_keyword, on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_content


__des__ = '缩写查询、梗百科'
__cmd__ = '''
1. {keyword} 是啥/是什么
2. 百科 {keyword}
'''.strip()
__short_cmd__ = 'xxx 是啥、百科xxx'
__example__ = '''
xswl 是啥
百科 洛天依
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


commands = {'是啥', '是什么', '是谁'}
what = on_keyword(commands, priority=27)
baike = on_command('baike', aliases={'百科'}, priority=17)


def split_command(msg):
    for command in commands:
        if command in msg:
            prefix, suffix = re.split(command, msg)
            return prefix, suffix
    return '', ''


@what.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.get_plaintext().strip().strip('.>,?!。，（）()[]【】')
    prefix_words = ['这', '这个', '那', '那个', '你', '我', '他', '它']
    suffix_words = ['意思', '梗', '玩意', '鬼']
    prefix, suffix = split_command(msg)
    if (not prefix or prefix in prefix_words) or \
            (suffix and suffix not in suffix_words):
        what.block = False
        return
    keyword = prefix

    less = False if event.is_tome() else True
    msg = await get_content(keyword, less=less)
    if msg:
        what.block = True
        await what.finish(msg)
    what.block = False
    return


@baike.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = event.get_plaintext().strip().strip('.>,?!。，（）()[]【】')
    if not keyword:
        await baike.finish()

    msg = await get_content(keyword, force=True)
    if msg:
        await baike.finish(msg)
    else:
        await baike.finish('找不到相关的条目')
