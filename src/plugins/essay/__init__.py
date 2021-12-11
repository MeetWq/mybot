from nonebot import on_shell_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_ussrjoke, get_cp_story, get_marketing_article


ussrjoke_help = '苏联笑话 {要讽刺的事} {谁提出来的} {有助于什么} {针对的是谁} {起作用范围}'
cpstory_help = 'CP文 {人物A} {人物B}'
marketing_help = '营销号 {主题} {描述} {另一种描述}'

__des__ = '多种短文生成'
__cmd__ = f'''
1、苏联笑话生成：{ussrjoke_help}
2、CP文生成：{cpstory_help}
3、营销号生成：{marketing_help}
'''.strip()
__short_cmd__ = '苏联笑话、CP文、营销号'
__example__ = '''
苏联笑话 996 马云 修福报 程序员 公司
CP文 攻 受
营销号 1+1 等于3 两个1加一起等于3
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


words_parser = ArgumentParser()
words_parser.add_argument('keyword', nargs='+')
ussrjoke = on_shell_command('ussrjoke', aliases={'苏联笑话'}, parser=words_parser, priority=28)
cpstory = on_shell_command('cpstory', aliases={'cp文', 'CP文'}, parser=words_parser, priority=28)
marketing = on_shell_command('marketing', aliases={'营销号'}, parser=words_parser, priority=28)


@ussrjoke.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'keyword') or len(args.keyword) != 5:
        await ussrjoke.finish(f'Usage:\n{ussrjoke_help}')

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
        await cpstory.finish(f'Usage:\n{cpstory_help}')

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
        await marketing.finish(f'Usage:\n{marketing_help}')

    keyword = args.keyword
    article = await get_marketing_article(keyword[0], keyword[1], keyword[2])
    if article:
        await marketing.finish(article)
    else:
        await marketing.finish('出错了，请稍后再试')
