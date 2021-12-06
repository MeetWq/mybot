import re
import time
import threading
from typing import Dict
from datetime import datetime, timedelta
from nonebot import require, get_driver, get_bots
from nonebot.adapters.cqhttp import Message, MessageSegment

from .data_source import get_live_info_by_uids, get_play_url, get_user_dynamics, get_dynamic_screenshot
from .live_status import get_sub_uids, get_status, update_status, get_sub_users, get_dynamic_users, get_record_users
from .dynamic import Dynamic
from .recorder import Recorder

from .config import Config
global_config = get_driver().config
blive_config = Config(**global_config.dict())

recorders: Dict[str, Recorder] = {}
last_time = {}


async def check_recorder(uid: str, info: dict):
    users = get_record_users(uid)
    if not users:
        if uid in recorders:
            recorder = recorders.pop(uid)
            recorder.recording = False
        return

    up_name = info['uname']
    room_id = info['room_id']
    status = info['live_status']
    if status == 1:
        if uid not in recorders or not recorders[uid].recording:
            play_url = await get_play_url(int(room_id))
            if not play_url:
                return
            if uid not in recorders:
                recorder = Recorder(up_name, play_url)
                recorders[uid] = recorder
            else:
                recorder = recorders[uid]
            thread = threading.Thread(target=recorder.record)
            thread.start()
            await send_record_msg(uid, f'{up_name} 录播启动...')
        else:
            recorder = recorders[uid]
            if recorder.need_update_url:
                play_url = await get_play_url(room_id)
                if play_url:
                    recorder.play_url = play_url
                    recorder.need_update_url = False
    else:
        if uid in recorders:
            recorder = recorders[uid]
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
                            msg = f'{up_name} 的录播文件：\n' + \
                                '\n'.join(recorder.urls)
                            await send_record_msg(uid, msg)
                        recorders.pop(uid)


def remove_unused_recorders(uids: list):
    for uid in recorders.keys():
        if uid not in uids:
            recorder = recorders.pop(uid)
            recorder.recording = False


async def check_dynamic(uid: str):
    users = get_dynamic_users(uid)
    if not users:
        return

    dynamics = await get_user_dynamics(uid)
    if len(dynamics) == 0:
        return

    if uid not in last_time:
        dynamic = Dynamic(dynamics[0])
        last_time[uid] = dynamic.time
        return

    for dynamic in dynamics[4::-1]:  # 从旧到新取最近5条动态
        dynamic = Dynamic(dynamic)
        if dynamic.time > last_time[uid] and dynamic.time > datetime.now().timestamp() - timedelta(minutes=10).seconds:
            img = await get_dynamic_screenshot(dynamic.url)
            if img:
                msg = dynamic.format_msg(img)
                await send_dynamic_msg(uid, msg)
                last_time[uid] = dynamic.time


async def live_monitor():
    uids = get_sub_uids()
    live_infos = await get_live_info_by_uids(uids)

    for uid in uids:
        if uid not in live_infos:
            continue
        info = live_infos[uid]
        status_old = get_status(uid)
        status = info['live_status']
        if status != status_old:
            update_status(uid, status)
            if status != 1 and status_old != 1:
                pass
            else:
                msg = live_msg(info)
                if msg:
                    await send_live_msg(uid, msg)
        await check_recorder(uid, info)
    remove_unused_recorders(uids)


def live_msg(info: dict):
    msg = None
    up_name = info['uname']
    status = info['live_status']
    if status == 1:
        start_time = time.strftime(
            "%y/%m/%d %H:%M:%S", time.localtime(info['live_time']))
        live_url = 'https://live.bilibili.com/' + str(info['room_id'])
        title = info['title']
        msg = Message()
        msg.append(
            f"{start_time}\n"
            f"{up_name} 开播啦！\n"
            f"{title}\n"
            f"直播间链接：{live_url}"
        )
        cover = info['cover_from_user']
        if cover:
            msg.append(MessageSegment.image(file=cover))
    elif status == 0:
        msg = f"{up_name} 下播了"
    elif status == 2:
        msg = f"{up_name} 下播了（轮播中）"
    return msg


async def dynamic_monitor():
    uids = get_sub_uids()
    for uid in uids:
        await check_dynamic(uid)


async def send_live_msg(uid: str, msg):
    users = get_sub_users(uid)
    for user_id in users:
        await send_bot_msg(user_id, msg)


async def send_dynamic_msg(uid: str, msg):
    users = get_dynamic_users(uid)
    for user_id in users:
        await send_bot_msg(user_id, msg)


async def send_record_msg(uid: str, msg):
    users = get_record_users(uid)
    for user_id in users:
        await send_bot_msg(user_id, msg)


async def send_bot_msg(user_id: str, msg):
    type, id = user_type(user_id)
    bots = list(get_bots().values())
    for bot in bots:
        if type == 'group':
            await bot.send_group_msg(group_id=id, message=msg)
        elif type == 'private':
            await bot.send_private_msg(user_id=id, message=msg)


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


scheduler = require("nonebot_plugin_apscheduler").scheduler

live_cron = blive_config.bilibili_live_cron
scheduler.add_job(
    live_monitor,
    'cron',
    second=live_cron[0],
    minute=live_cron[1],
    hour=live_cron[2],
    day=live_cron[3],
    month=live_cron[4],
    year=live_cron[5],
    id='bilibili_live_cron',
    coalesce=True,
    misfire_grace_time=30
)

dynamic_cron = blive_config.bilibili_dynamic_cron
scheduler.add_job(
    dynamic_monitor,
    'cron',
    second=dynamic_cron[0],
    minute=dynamic_cron[1],
    hour=dynamic_cron[2],
    day=dynamic_cron[3],
    month=dynamic_cron[4],
    year=dynamic_cron[5],
    id='bilibili_dynamic_cron',
    coalesce=True,
    misfire_grace_time=30
)
