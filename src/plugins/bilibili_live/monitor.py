from pathlib import Path
from nonebot import require, get_bots
from nonebot.adapters.cqhttp import Message, MessageSegment

from .sub_list import get_sub_list
from .data_source import get_live_info
from .live_status import load_status_list, update_status

status_path = Path() / 'data' / 'bilibili_live' / 'live_status.json'


async def bilibili_live_monitor():
    msg_dict = {}
    status_list = load_status_list()
    for room_id, status in status_list.items():
        info = await get_live_info(room_id)
        if info['status'] != status:
            msg_dict[room_id] = format_msg(info)
            update_status(room_id, info['status'])
    if not msg_dict:
        return
    bots = list(get_bots().values())
    for bot in bots:
        noitce_groups = []
        npm = require('nonebot_plugin_manager')
        group_list = await bot.get_group_list()
        for group in group_list:
            group_id = str(group['group_id'])
            group_plugin_list = npm.get_group_plugin_list(group_id)
            if group_plugin_list['bilibili_live']:
                noitce_groups.append(group_id)

        for group_id in noitce_groups:
            group_sub_list = get_sub_list(group_id)
            for room_id in group_sub_list.keys():
                if room_id in msg_dict:
                    msg = msg_dict[room_id]
                    if msg:
                        await bot.send_group_msg(group_id=group_id, message=msg)


def format_msg(info: dict) -> Message:
    msg = ''
    if info['status'] == 0:
        msg = f"{info['up_name']} 下播了"
    elif info['status'] == 1:
        msg = Message()
        msg.append(f"{info['time']}\n{info['up_name']}开播啦！\n{info['title']}\n直播间链接：{info['url']}")
        cover = info['cover']
        if cover:
            msg.append(MessageSegment.image(file=cover))
    elif info['status'] == 2:
        msg = f"{info['up_name']}下播了（轮播中）"
    return msg


scheduler = require("nonebot_plugin_apscheduler").scheduler

scheduler.add_job(
    bilibili_live_monitor,
    'cron',
    hour='9-23',
    minute='*/2',
    id='bilibili_live_monitor_in_day',
    coalesce=True,
    misfire_grace_time=30
)

scheduler.add_job(
    bilibili_live_monitor,
    'cron',
    hour='0-8',
    minute='*/10',
    id='bilibili_live_monitor_in_night',
    coalesce=True,
    misfire_grace_time=30
)
