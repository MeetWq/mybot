import re
import threading
from typing import Dict
from nonebot import require, get_driver, get_bots
from nonebot.adapters.cqhttp import Message, MessageSegment

from .sub_list import get_sub_list
from .data_source import get_live_status, get_live_info, get_play_url
from .live_status import get_status_list, update_status
from .recorder import Recorder

from .config import Config
global_config = get_driver().config
blive_config = Config(**global_config.dict())

recorders: Dict[str, Recorder] = {}


def has_record(room_id: str):
    sub_list = get_sub_list()
    for _, user_sub_list in sub_list.items():
        if room_id in user_sub_list and user_sub_list[room_id]['record']:
            return True
    return False


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


async def send_bot_msg(user_id: str, msg: str):
    type, id = user_type(user_id)
    bots = list(get_bots().values())
    for bot in bots:
        if type == 'group':
            await bot.send_group_msg(group_id=id, message=msg)
        elif type == 'private':
            await bot.send_private_msg(user_id=id, message=msg)


async def send_record_msg(room_id: str, msg: str):
    if not msg:
        return
    sub_list = get_sub_list()
    for user_id, user_sub_list in sub_list.items():
        if room_id in user_sub_list and user_sub_list[room_id]['record']:
            await send_bot_msg(user_id, msg)


async def check_recorders():
    status_list = get_status_list()
    for room_id, status in status_list.items():
        if not has_record(room_id):
            if room_id in recorders:
                recorder = recorders.pop(room_id)
                recorder.recording = False
            continue

        if status == 1:
            if room_id not in recorders or not recorders[room_id].recording:
                play_url = await get_play_url(room_id)
                info = await get_live_info(room_id)
                up_name = info['up_name']
                if play_url:
                    recorder = Recorder(up_name, play_url)
                    recorders[room_id] = recorder
                    thread = threading.Thread(target=recorder.record)
                    thread.start()
                    await send_record_msg(room_id, f'{up_name} 录制启动...')
            else:
                recorder = recorders[room_id]
                if recorder.need_update_url:
                    play_url = await get_play_url(room_id)
                    if play_url:
                        recorder.play_url = play_url
                        recorder.need_update_url = False
        else:
            if room_id in recorders:
                recorder = recorders[room_id]
                if recorder.recording:
                    recorder.recording = False
                    if not recorder.uploading:
                        thread = threading.Thread(target=recorder.upload)
                        thread.start()
                else:
                    if not recorder.uploading:
                        if recorder.files:
                            thread = threading.Thread(target=recorder.upload)
                            thread.start()
                        else:
                            if recorder.urls:
                                msg = f'{recorder.up_name} 的录播文件：\n' + \
                                    '\n'.join(recorder.urls)
                                await send_record_msg(room_id, msg)
                            recorders.pop(room_id)


async def blive_monitor():
    msg_dict = {}
    status_list = get_status_list()
    for room_id, status in status_list.items():
        live_status = await get_live_status(room_id)
        if live_status != status:
            update_status(room_id, live_status)
            info = await get_live_info(room_id)
            msg = None
            if info['status'] == 1:
                msg = Message()
                msg.append(
                    f"{info['time']}\n{info['up_name']} 开播啦！\n{info['title']}\n直播间链接：{info['url']}")
                cover = info['cover']
                if cover:
                    msg.append(MessageSegment.image(file=cover))
            elif status == 1:
                if info['status'] == 0:
                    msg = f"{info['up_name']} 下播了"
                elif info['status'] == 2:
                    msg = f"{info['up_name']} 下播了（轮播中）"
            if msg:
                msg_dict[room_id] = msg

    if msg_dict:
        sub_list = get_sub_list()
        for user_id, user_sub_list in sub_list.items():
            for room_id in user_sub_list.keys():
                if room_id in msg_dict:
                    msg = msg_dict[room_id]
                    if not msg:
                        continue
                    await send_bot_msg(user_id, msg)

    await check_recorders()


scheduler = require("nonebot_plugin_apscheduler").scheduler

cron_day = blive_config.blive_cron_day
scheduler.add_job(
    blive_monitor,
    'cron',
    second=cron_day[0],
    minute=cron_day[1],
    hour=cron_day[2],
    day=cron_day[3],
    month=cron_day[4],
    year=cron_day[5],
    id='blive_monitor_in_day',
    coalesce=True,
    misfire_grace_time=30
)

cron_night = blive_config.blive_cron_night
scheduler.add_job(
    blive_monitor,
    'cron',
    second=cron_night[0],
    minute=cron_night[1],
    hour=cron_night[2],
    day=cron_night[3],
    month=cron_night[4],
    year=cron_night[5],
    id='blive_monitor_in_night',
    coalesce=True,
    misfire_grace_time=30
)
