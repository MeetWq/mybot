import threading
from nonebot import require, get_driver
from nonebot.adapters.cqhttp import Message, MessageSegment

from .sub_list import get_sub_list
from .data_source import get_live_status, get_live_info
from .live_status import get_status_list, update_status
from .utils import send_bot_msg
from .recorder import Recorder

from .config import Config
global_config = get_driver().config
blive_config = Config(**global_config.dict())

recorders = {}


async def blive_monitor():
    msg_dict = {}
    status_list = get_status_list()
    for room_id, status in status_list.items():
        live_status = await get_live_status(room_id)
        if live_status != status:
            update_status(room_id, live_status)
            info = await get_live_info(room_id)
            msg_dict[room_id] = format_msg(info)
            await check_recorder(room_id, info)

    if not msg_dict:
        return

    sub_list = get_sub_list()
    for user_id, user_sub_list in sub_list.items():
        for room_id in user_sub_list.keys():
            if room_id in msg_dict:
                msg = msg_dict[room_id]
                if not msg:
                    continue
                await send_bot_msg(user_id, msg)


def format_msg(info: dict) -> Message:
    msg = ''
    if info['status'] == 0:
        msg = f"{info['up_name']} 下播了"
    elif info['status'] == 1:
        msg = Message()
        msg.append(
            f"{info['time']}\n{info['up_name']} 开播啦！\n{info['title']}\n直播间链接：{info['url']}")
        cover = info['cover']
        if cover:
            msg.append(MessageSegment.image(file=cover))
    elif info['status'] == 2:
        msg = f"{info['up_name']} 下播了（轮播中）"
    return msg


class RecordThread(threading.Thread):
    def __init__(self, recorder):
        threading.Thread.__init__(self)
        self.recorder = recorder

    def run(self):
        self.recorder.record()


class UploadThread(threading.Thread):
    def __init__(self, recorder):
        threading.Thread.__init__(self)
        self.recorder = recorder

    def run(self):
        self.recorder.stop_and_upload()


async def check_recorder(room_id: str, info: dict):
    has_record = False
    sub_list = get_sub_list()
    for _, user_sub_list in sub_list.items():
        if room_id in user_sub_list and user_sub_list[room_id]['record']:
            has_record = True
            break
    if not has_record:
        return
    if info['status'] == 1:
        if room_id not in recorders:
            recorders[room_id] = Recorder(info['up_name'], room_id)
        thread = RecordThread(recorders[room_id])
        thread.start()
    else:
        if room_id not in recorders or not recorders[room_id].recording:
            return
        thread = UploadThread(recorders[room_id])
        thread.start()


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
