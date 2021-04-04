from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import GroupMessageEvent

from .monitor import *
from .data_source import get_live_info
from .live_status import update_status_list
from .sub_list import get_sub_list, clear_sub_list, add_sub_list, del_sub_list

export = export()
export.description = 'B站直播间订阅'
export.usage = '''Usage:
B站直播间 订阅 {房间号/用户名}
B站直播间 取消订阅 {房间号/用户名}
B站直播间 清空订阅
B站直播间 订阅列表'''
export.notice = 'Notice:\n管理订阅需要群管理员权限'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

bilibili_live = on_command('bilibili_live', aliases={'B站直播间', 'b站直播间'}, priority=35)


@bilibili_live.handle()
@bilibili_live.args_parser
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    args = str(event.get_plaintext()).strip().split()
    if not args:
        await bilibili_live.finish(export.usage + '\n' + export.notice)
    state['args'] = args


@bilibili_live.got('args')
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    args = state['args']
    if len(args) == 1:
        state['command'] = args[0]
    elif len(args) == 2:
        state['command'] = args[0]
        state['room_id'] = args[1]
    else:
        await bilibili_live.finish('参数数量错误\n' + export.usage)


@bilibili_live.got('command')
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    command = state['command']
    if command not in ['订阅', '取消订阅', '订阅列表', '清空订阅', 'd', 'td', 'list', 'clear']:
        await bilibili_live.finish('没有这个命令哦\n' + export.usage)

    group_id = str(event.group_id)
    if command in ['订阅列表', 'list']:
        sub_list = get_sub_list(group_id)
        if not sub_list:
            await bilibili_live.finish('本群还没有任何订阅')
        msg = '本群已订阅以下直播间:\n'
        for room_id, up_name in sub_list.items():
            msg += f'\n{up_name} ({room_id})'
        await bilibili_live.send(message=msg)
        await bilibili_live.finish()
    elif command in ['清空订阅', 'clear']:
        if not check_permission(bot, event):
            await bilibili_live.finish('管理订阅需要群管理员权限')
        clear_sub_list(group_id)
        await update_status_list()
        await bilibili_live.finish('本群订阅列表已清空')
    else:
        if not check_permission(bot, event):
            await bilibili_live.finish('管理订阅需要群管理员权限')


@bilibili_live.got('room_id', prompt='请输入房间号或主播名称')
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    command = state['command']
    room_id = state['room_id']
    group_id = str(event.group_id)

    if room_id.isdigit():
        info = await get_live_info(room_id=room_id)
        if not info:
            await bilibili_live.finish('获取直播间信息失败，请检查名称或稍后再试')
    else:
        up_name = room_id
        info = await get_live_info(up_name=up_name)
        if not info:
            await bilibili_live.finish('获取直播间信息失败，请检查名称或稍后再试')

    room_id = info['room_id']
    up_name = info['up_name']

    if command in ['订阅', 'd']:
        status = add_sub_list(group_id, room_id, up_name)
        if status == 'success':
            await update_status_list()
            await bilibili_live.finish(f"成功订阅 {info['up_name']} 的直播间")
        elif status == 'dupe':
            await bilibili_live.finish('已经订阅该主播，请不要重复添加')
        else:
            await bilibili_live.finish('出错了，请稍后再试')
    elif command in ['取消订阅', 'td']:
        status = del_sub_list(group_id, room_id)
        if status == 'success':
            await update_status_list()
            await bilibili_live.finish(f"成功取消订阅 {info['up_name']} 的直播间")
        elif status == 'dupe':
            await bilibili_live.finish('尚未订阅该主播')
        else:
            await bilibili_live.finish('出错了，请稍后再试')


def check_permission(bot: Bot, event: GroupMessageEvent):
    return event.sender.role in ['admin', 'owner'] or event.get_user_id() in bot.config.superusers
