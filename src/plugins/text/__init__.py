from nonebot import export, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_text

export = export()
export.description = '多种文本生成'
export.usage = 'Usage:\n  text [options] {text}'
export.options = 'Options:\n  -t, --type 文本类型，目前支持：抽象话(0)、火星文(1)、蚂蚁文(2)、翻转文字(3)、故障文字(4)'
export.notice = 'Notice:\n  抽象话只支持中文；翻转文字只支持英文'
export.help = export.description + '\n' + export.usage + '\n' + export.options + '\n' + export.notice

text_parser = ArgumentParser()
text_parser.add_argument('-t', '--type', type=int)
text_parser.add_argument('text', nargs='+')

text = on_shell_command('text', parser=text_parser, priority=19)


@text.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'text'):
        await text.finish()

    type = args.type
    if type not in [0, 1, 2, 3, 4]:
        await text.finish()

    texts = args.text
    texts = ' '.join(texts)
    result = await get_text(texts, type)
    if result:
        await text.finish(result)
    else:
        await text.finish('出错了，请稍后再试')
