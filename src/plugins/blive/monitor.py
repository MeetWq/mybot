import re
import threading
from typing import Dict
from datetime import datetime, timedelta
from nonebot import require, get_driver, get_bots
from nonebot.log import logger

from .data_source import get_live_info_by_uids, get_play_url, get_user_dynamics
from .uid_list import get_sub_uids, get_sub_users, get_dynamic_users, get_record_users
from .dynamic import Dynamic
from .live_info import LiveInfo
from .recorder import Recorder
from .aliyun import update_refresh_token

from .config import Config

blive_config = Config.parse_obj(get_driver().config.dict())

recorders: Dict[str, Recorder] = {}
live_status = {}
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
            msg = await dynamic.format_msg()
            if msg:
                await send_dynamic_msg(uid, msg)
            last_time[uid] = dynamic.time


async def dynamic_monitor():
    uids = get_sub_uids()
    for uid in uids:
        await check_dynamic(uid)


async def live_monitor():
    uids = get_sub_uids()
    if not uids:
        return
    live_infos = await get_live_info_by_uids(uids)

    for uid in uids:
        if uid not in live_infos:
            continue
        info = live_infos[uid]
        status = info['live_status']
        if uid not in live_status:
            live_status[uid] = status
            continue
        if status != live_status[uid]:
            if status != 1 and live_status[uid] != 1:
                pass
            else:
                msg = await LiveInfo(info).format_msg()
                if msg:
                    await send_live_msg(uid, msg)
            live_status[uid] = status
        await check_recorder(uid, info)
    remove_unused_recorders(uids)


def remove_unused_recorders(uids: list):
    for uid in recorders.keys():
        if uid not in uids:
            recorder = recorders.pop(uid)
            recorder.recording = False


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
        try:
            if type == 'group':
                await bot.send_group_msg(group_id=id, message=msg)
            elif type == 'private':
                await bot.send_private_msg(user_id=id, message=msg)
        except:
            logger.warning(f"send msg failed, user_id: {user_id}, msg: {msg}")
            continue


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

token_cron = blive_config.aliyunpan_update_token_cron
scheduler.add_job(
    update_refresh_token,
    'cron',
    second=token_cron[0],
    minute=token_cron[1],
    hour=token_cron[2],
    day=token_cron[3],
    month=token_cron[4],
    year=token_cron[5],
    id='aliyunpan_update_token_cron',
    coalesce=True,
    misfire_grace_time=3600
)
