from nonebot import on_shell_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent

from .rss_class import RSS
from .monitor import *
from .data_source import update_rss_info
from .rss_list import get_rss_list, clear_rss_list, add_rss_list, del_rss_list


__des__ = 'RSS订阅'
__cmd__ = '''
添加订阅：rss add {订阅名} {RSSHub路径/完整URL}
取消订阅：rss del {订阅名}
订阅列表：rss list
清空订阅：rss clear
'''.strip()
__example__ = '''
rss add /bilibili/user/dynamic/282994
rss add https://rsshub.app/bilibili/user/dynamic/282994
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


rss_parser = ArgumentParser()
rss_parser.add_argument('arg', nargs='+')
rss = on_shell_command('rss', parser=rss_parser, priority=12)


@rss.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'arg'):
        await rss.finish()
    state['arg'] = args.arg


@rss.got('arg')
async def _(bot: Bot, event: Event, state: T_State):
    args = state['arg']
    if len(args) >= 1:
        state['command'] = args[0]
    if len(args) >= 2:
        state['name'] = args[1]
    if len(args) == 3:
        state['url'] = args[2]
    if len(args) < 1:
        await rss.finish()
    elif len(args) > 3:
        await rss.finish(f'Usage:\n{__cmd__}')


def get_id(event: Event):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.get_user_id())


@rss.got('command')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    if command not in ['添加', '删除', '列表', '清空', 'add', 'del', 'list', 'clear']:
        await rss.finish()

    user_id = get_id(event)
    state['user_id'] = user_id
    if command in ['列表', 'list']:
        rss_list = get_rss_list(user_id)
        if not rss_list:
            await rss.finish('目前还没有任何订阅')
        msg = '已订阅以下内容:\n'
        for r in rss_list:
            msg += f'\n{r.name} ({r.url})'
        await rss.finish(msg)
    elif command in ['清空', 'clear']:
        clear_rss_list(user_id)
        await rss.finish('订阅列表已清空')


@rss.got('name', prompt='请输入订阅名')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    name = state['name']
    user_id = state['user_id']

    if command in ['删除', 'del']:
        status = del_rss_list(user_id, name)
        if status == 'success':
            await rss.finish(f"成功删除订阅 {name}")
        elif status == 'dupe':
            await rss.finish('还没有该名称的订阅')
        else:
            await rss.finish('出错了，请稍后再试')


@rss.got('url', prompt='请输入订阅链接')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    name = state['name']
    url = state['url']
    user_id = state['user_id']

    if command not in ['添加', 'add']:
        await rss.finish()

    new_rss = RSS(name, url)
    status = await update_rss_info(new_rss)
    if not status:
        await rss.finish('获取RSS信息失败，请检查链接或稍后再试')

    status = add_rss_list(user_id, new_rss)
    if status == 'success':
        await rss.finish(f"成功添加订阅 {name}：{new_rss.title}")
    elif status == 'dupe':
        await rss.finish('已存在该名称的订阅，请更换名称或删除之前的订阅')
    else:
        await rss.finish('出错了，请稍后再试')
