import re
from nonebot import export, on_keyword, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, Message

from .data_source import get_content

export = export()
export.description = '百科'
export.usage = 'Usage:\n  1. what [options] {keyword}\n  2. {keyword}是啥/是什么'
export.options = 'Options:\n  -s, --source 百科来源，目前支持：nbnhhsh、小鸡词典(jiki)、百度百科(baidu)、维基百科(wiki)'
export.notice = 'Notice:\n  为避免影响正常聊天，“是啥”仅当词条完全匹配时才会响应。若要返回相近的结果请用“what”命令'
export.help = export.description + '\n' + export.usage + '\n' + export.options + '\n' + export.notice

what_parser = ArgumentParser()
what_parser.add_argument('-s', '--source', default='all')
what_parser.add_argument('keyword', nargs='+')

commands = {'是啥', '是什么', '是谁'}
what = on_keyword(commands, priority=25)
what_command = on_shell_command('what', parser=what_parser, priority=17)

sources = ['nbnhhsh', 'jiki', 'baidu', 'wiki']


def split_command(msg):
    for command in commands:
        if command in msg:
            prefix, suffix = re.split(command, msg)
            return prefix, suffix
    return '', ''


@what.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip().strip('.>,?!。，（）()[]【】')
    prefix_words = ['这', '这个', '那', '那个']
    suffix_words = ['意思', '梗', '玩意', '鬼']
    prefix, suffix = split_command(msg)
    if not prefix or prefix in prefix_words:
        what.block = False
        return
    if suffix and suffix not in suffix_words:
        what.block = False
        return
    keyword = prefix

    for source in sources:
        msg = await get_content(keyword, source)
        if msg:
            what.block = True
            await what.send(message=msg)
            await what.finish()
    what.block = False
    return


@what_command.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'keyword'):
        await what_command.finish(export.usage)
    keyword = args.keyword
    keyword = ' '.join(keyword)
    keyword = keyword.strip().strip('.>,?!。，（）()[]【】')
    if not keyword:
        await what_command.finish(export.usage)

    await what_command.send(message='请稍候...')
    source = args.source
    if source == 'all':
        for s in sources:
            msg = await get_content(keyword, s, force=True)
            if msg:
                await what_command.send(message=msg)
                await what_command.finish()
        await what_command.finish('找不到相关的条目')
    elif source not in sources:
        await what_command.finish(export.options)
    else:
        msg = await get_content(keyword, source, force=True)
        if msg:
            await what_command.send(message=msg)
            await what_command.finish()
        await what_command.finish(source + '中找不到相关的条目')
