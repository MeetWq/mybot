import re
from pathlib import Path
from nonebot import require, get_bots, get_driver
from nonebot.adapters.cqhttp import Message, MessageSegment

from .sub_list import load_sub_list
from .data_source import get_live_info
from .live_status import load_status_list, update_status

from .config import Config
global_config = get_driver().config
bilibili_live_config = Config(**global_config.dict())

status_path = Path() / 'data' / 'bilibili_live' / 'live_status.json'


def user_type(user_id: str):
    p_group = r'group_(\d+)'
    p_private = r'private_(\d+)'
    match = re.fullmatch(p_group, user_id)
    if match:
        return 'group', match.group(1)
    match = re.fullmatch(p_private, user_id)
    if match:
        return 'private', match.group(1)
    return '', user_id


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
        sub_list = load_sub_list()
        for user_id, user_sub_list in sub_list.items():
            for room_id in user_sub_list.keys():
                if room_id in msg_dict:
                    msg = msg_dict[room_id]
                    if not msg:
                        continue
                    type, id = user_type(user_id)
                    if type == 'group':
                        await bot.send_group_msg(group_id=id, message=msg)
                    elif type == 'private':
                        await bot.send_private_msg(user_id=id, message=msg)


def format_msg(info: dict) -> Message:
    msg = ''
    if info['status'] == 0:
        msg = f"{info['up_name']} 下播了"
    elif info['status'] == 1:
        msg = Message()
        msg.append(f"{info['time']}\n{info['up_name']} 开播啦！\n{info['title']}\n直播间链接：{info['url']}")
        cover = info['cover']
        if cover:
            msg.append(MessageSegment.image(file=cover))
    elif info['status'] == 2:
        msg = f"{info['up_name']} 下播了（轮播中）"
    return msg


scheduler = require("nonebot_plugin_apscheduler").scheduler

cron_day = bilibili_live_config.bilibili_live_cron_day
scheduler.add_job(
    bilibili_live_monitor,
    'cron',
    second=cron_day[0],
    minute=cron_day[1],
    hour=cron_day[2],
    day=cron_day[3],
    month=cron_day[4],
    year=cron_day[5],
    id='bilibili_live_monitor_in_day',
    coalesce=True,
    misfire_grace_time=30
)

cron_night = bilibili_live_config.bilibili_live_cron_night
scheduler.add_job(
    bilibili_live_monitor,
    'cron',
    second=cron_night[0],
    minute=cron_night[1],
    hour=cron_night[2],
    day=cron_night[3],
    month=cron_night[4],
    year=cron_night[5],
    id='bilibili_live_monitor_in_night',
    coalesce=True,
    misfire_grace_time=30
)
