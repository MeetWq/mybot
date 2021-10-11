from nonebot import export, on_shell_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_ussrjoke, get_cp_story, get_marketing_article

export = export()
export.description = '多种对话生成'
ussrjoke_help = '苏联笑话生成 {要讽刺的事情是} {这件事是谁提出来的} {提出者声称这件事有助于什么} {这件事针对的是哪些人} {这件事起作用的范围}'
cpstory_help = 'CP文生成 {人物A} {人物B}'
marketing_help = '营销号生成 {主题} {描述} {另一种描述}'
export.usage = f'Usage:\n  1、{ussrjoke_help}\n\n  2、{cpstory_help}\n\n  3、{marketing_help}'
export.help = export.description + '\n' + export.usage

words_parser = ArgumentParser()
words_parser.add_argument('keyword', nargs='+')
ussrjoke = on_shell_command('ussrjoke', aliases={'苏联笑话生成'}, parser=words_parser, priority=28)
cpstory = on_shell_command('cpstory', aliases={'cp文生成', 'CP文生成'}, parser=words_parser, priority=28)
marketing = on_shell_command('marketing', aliases={'营销号生成'}, parser=words_parser, priority=28)


@ussrjoke.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'keyword') or len(args.keyword) != 5:
        await ussrjoke.finish('Usage:\n  ' + ussrjoke_help)

    keyword = args.keyword
    joke = await get_ussrjoke(keyword[0], keyword[1], keyword[2], keyword[3], keyword[4])
    if joke:
        await ussrjoke.finish(joke)
    else:
        await ussrjoke.finish('出错了，请稍后再试')


@cpstory.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'keyword') or len(args.keyword) != 2:
        await cpstory.finish('Usage:\n  ' + cpstory_help)

    keyword = args.keyword
    story = await get_cp_story(keyword[0], keyword[1])
    if story:
        await cpstory.finish(story)
    else:
        await cpstory.finish('出错了，请稍后再试')


@marketing.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'keyword') or len(args.keyword) != 3:
        await marketing.finish('Usage:\n  ' + marketing_help)

    keyword = args.keyword
    article = await get_marketing_article(keyword[0], keyword[1], keyword[2])
    if article:
        await marketing.finish(article)
    else:
        await marketing.finish('出错了，请稍后再试')
