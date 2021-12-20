from nonebot import on_shell_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event

from .data_source import translate


__des__ = '翻译'
__cmd__ = '''
@我 trans/翻译 [options] {text}
Options:
-e --engine: 翻译引擎，支持：baidu (default), youdao, google, bing
-s --source：源语言，默认为 自动检测(auto)
-t --target：目标语言，默认为 中文(zh)
'''.strip()
__short_cmd__ = '@我 翻译 {text}'
__example__ = '''
@小Q 翻译 hello
@小Q trans -e youdao hello
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


parser = ArgumentParser()
parser.add_argument('-e', '--engine', default='baidu')
parser.add_argument('-s', '--source', default='auto')
parser.add_argument('-t', '--target', default='zh')
parser.add_argument('text')

trans = on_shell_command(
    'trans', aliases={'translate', '翻译'}, parser=parser, priority=11)


@trans.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']

    if not hasattr(args, 'text') or not args.text:
        await trans.finish()

    result = await translate(args.text, args.engine, args.source, args.target)
    if result:
        await trans.finish(result)
    else:
        await trans.finish('出错了，请稍后再试')
