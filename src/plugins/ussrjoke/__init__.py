from nonebot import export, on_shell_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_ussrjoke

export = export()
export.description = '苏联笑话生成'
export.usage = 'Usage:\n  苏联笑话生成 {要讽刺的事情是} {这件事是谁提出来的} {提出者声称这件事有助于什么} {这件事针对的是哪些人} {这件事起作用的范围}'
export.notice = 'Notice:\n  需完整填写5项内容，用空格分开'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

joke_parser = ArgumentParser()
joke_parser.add_argument('keyword', nargs='+')

ussrjoke = on_shell_command('ussrjoke', aliases={'苏联笑话生成'}, parser=joke_parser, priority=32)


@ussrjoke.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'keyword'):
        await ussrjoke.finish(export.usage)

    keyword = args.keyword
    if len(keyword) != 5:
        await ussrjoke.finish(export.usage + '\n' + export.notice)

    joke = await get_ussrjoke(keyword[0], keyword[1], keyword[2], keyword[3], keyword[4])
    if joke:
        await ussrjoke.send(message=joke)
        await ussrjoke.finish()
    else:
        await ussrjoke.finish('出错了，请稍后重试')
