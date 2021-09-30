from nonebot import export, on_shell_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent

from .monitor import *
from .data_source import get_live_info
from .live_status import update_status_list
from .sub_list import get_sub_list, clear_sub_list, add_sub_list, del_sub_list, open_record, close_record


export = export()
export.description = 'B站直播间订阅'
export.usage = '''Usage:
添加订阅：blive d {房间号/用户名}
取消订阅：blive td {房间号/用户名}
订阅列表：blive list
清空订阅：blive clear
自动录制：blive record {房间号/用户名} on/off'''
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
    if len(args) >= 2:
        state['room_id'] = args[1]
    if len(args) == 3:
        state['action'] = args[2]
    if len(args) > 3:
        await blive.finish(export.usage)


def get_id(event: Event):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.get_user_id())


@blive.got('command')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    if command not in ['订阅', '取消订阅', '订阅列表', '清空订阅', '录制', 'd', 'td', 'list', 'clear', 'record']:
        await blive.finish('没有这个命令哦\n' + export.usage)

    user_id = get_id(event)
    state['user_id'] = user_id
    if command in ['订阅列表', 'list']:
        sub_list = get_sub_list(user_id)
        if not sub_list:
            await blive.finish('目前还没有任何订阅')
        msg = '已订阅以下直播间:\n'
        for room_id, info in sub_list.items():
            msg += f"\n{info['up_name']} ({room_id})"
        await blive.finish(msg)
    elif command in ['清空订阅', 'clear']:
        clear_sub_list(user_id)
        await update_status_list()
        await blive.finish('订阅列表已清空')


@blive.got('room_id', prompt='请输入房间号或主播名称')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    room_id = state['room_id']
    user_id = state['user_id']

    if command not in ['订阅', '取消订阅', 'd', 'td']:
        if 'action' not in state.keys():
            await blive.finish(export.usage)
        return

    if room_id.isdigit():
        info = await get_live_info(room_id=room_id)
    else:
        up_name = room_id
        info = await get_live_info(up_name=up_name)
    if not info:
        await blive.finish('获取直播间信息失败，请检查名称或稍后再试')

    room_id = info['room_id']
    up_name = info['up_name']

    if command in ['订阅', 'd']:
        status = add_sub_list(user_id, room_id, up_name)
        if status == 'success':
            await update_status_list()
            await blive.finish(f"成功订阅 {info['up_name']} 的直播间")
        elif status == 'dupe':
            await blive.finish('已经订阅该主播，请不要重复添加')
        else:
            await blive.finish('出错了，请稍后再试')
    elif command in ['取消订阅', 'td']:
        status = del_sub_list(user_id, room_id)
        if status == 'success':
            await update_status_list()
            await blive.finish(f"成功取消订阅 {info['up_name']} 的直播间")
        elif status == 'dupe':
            await blive.finish('尚未订阅该主播')
        else:
            await blive.finish('出错了，请稍后再试')


@blive.got('action')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    room_id = state['room_id']
    user_id = state['user_id']
    action = state['action']

    if command in ['录制', 'record']:
        sub_list = get_sub_list(user_id)
        room_id_real = ''
        if room_id.isdigit():
            if room_id in sub_list:
                room_id_real = room_id
        else:
            for id, info in sub_list.items():
                if room_id == info['up_name']:
                    room_id_real = id
                    break
        if not room_id_real:
            await blive.finish('尚未订阅该主播，先d了再说')

        if action not in ['on', 'off']:
            await blive.finish('Usage: blive record {房间号/用户名} on/off')

        up_name = sub_list[room_id_real]['up_name']
        if action in ['on']:
            open_record(user_id, room_id_real)
            await blive.finish(f'{up_name} 自动录制已打开')
        elif action in ['off']:
            close_record(user_id, room_id_real)
            await blive.finish(f'{up_name} 自动录制已关闭')
    else:
        await blive.finish(export.usage)
