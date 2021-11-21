from nonebot import export, on_shell_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent

from .monitor import *
from .data_source import get_live_info
from .sub_list import get_sub_list, clear_sub_list, add_sub_list, del_sub_list, open_record, close_record


export = export()
export.description = 'B站直播间订阅'
export.usage = '''Usage:
添加订阅：blive d {用户名/UID}
取消订阅：blive td {用户名/UID}
订阅列表：blive list
清空订阅：blive clear
自动录播：blive rec {用户名/UID}
取消录播：blive recoff {用户名/UID}'''
export.help = export.description + '\n' + export.usage


blive_parser = ArgumentParser()
blive_parser.add_argument('arg', nargs='+')
blive = on_shell_command('blive', aliases={
                         'bilibili_live', 'B站直播间', 'b站直播间'}, parser=blive_parser, priority=35)


@blive.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'arg'):
        await blive.finish(export.usage)
    state['arg'] = args.arg


@blive.got('arg')
async def _(bot: Bot, event: Event, state: T_State):
    args = state['arg']
    if len(args) >= 1:
        state['command'] = args[0]
    if len(args) == 2:
        state['name'] = args[1]
    if len(args) > 2:
        await blive.finish(export.usage)


def get_id(event: Event):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.get_user_id())


@blive.got('command')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    if command not in ['订阅', '取消订阅', '订阅列表', '清空订阅', '录播', '取消录播', 'd', 'td', 'list', 'clear', 'rec', 'recoff']:
        await blive.finish('没有这个命令哦\n' + export.usage)

    user_id = get_id(event)
    state['user_id'] = user_id
    if command in ['订阅列表', 'list']:
        sub_list = get_sub_list(user_id)
        if not sub_list:
            await blive.finish('目前还没有任何订阅')
        msg = '已订阅以下直播间:\n'
        for _, info in sub_list.items():
            msg += f"\n{info['up_name']} {'(自动录播)' if info['record'] else ''}"
        await blive.finish(msg)
    elif command in ['清空订阅', 'clear']:
        clear_sub_list(user_id)
        await blive.finish('订阅列表已清空')


@blive.got('name', prompt='请输入房间号或主播名称')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    name = state['name']
    user_id = state['user_id']

    if name.isdigit():
        info = await get_live_info(uid=name)
    else:
        info = await get_live_info(up_name=name)
    if not info:
        await blive.finish('获取直播间信息失败，请检查名称或稍后再试')

    uid = str(info['uid'])
    up_name = info['uname']

    if command in ['订阅', 'd']:
        status = add_sub_list(user_id, uid, info)
        if status == 'success':
            await blive.finish(f"成功订阅 {up_name} 的直播间")
        elif status == 'dupe':
            await blive.finish('已经订阅该主播')
        else:
            await blive.finish('出错了，请稍后再试')
    elif command in ['取消订阅', 'td']:
        status = del_sub_list(user_id, uid)
        if status == 'success':
            await blive.finish(f"成功取消订阅 {up_name} 的直播间")
        elif status == 'dupe':
            await blive.finish('尚未订阅该主播')
        else:
            await blive.finish('出错了，请稍后再试')
    elif command in ['录播', 'rec']:
        status = open_record(user_id, uid)
        if status == 'success':
            await blive.finish(f'{up_name} 自动录播已打开')
        elif status == 'dupe':
            await blive.finish('尚未订阅该主播')
        else:
            await blive.finish('出错了，请稍后再试')
    elif command in ['取消录播', 'recoff']:
        status = close_record(user_id, uid)
        if status == 'success':
            await blive.finish(f'{up_name} 自动录播已关闭')
        elif status == 'dupe':
            await blive.finish('尚未订阅该主播')
        else:
            await blive.finish('出错了，请稍后再试')
