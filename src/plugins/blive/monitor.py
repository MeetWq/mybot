from datetime import datetime, timedelta
from nonebot import get_driver
from nonebot_plugin_apscheduler import scheduler

from .data_source import get_user_dynamics
from .uid_list import get_sub_uids, get_dynamic_users
from .send_msg import send_dynamic_msg
from .models import Dynamic
from .config import Config


last_time = {}


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
        if (
            dynamic.time > last_time[uid]
            and dynamic.time
            > datetime.now().timestamp() - timedelta(minutes=10).seconds
        ):
            msg = await dynamic.format_msg()
            if msg:
                await send_dynamic_msg(uid, msg)
            last_time[uid] = dynamic.time


async def dynamic_monitor():
    uids = get_sub_uids()
    for uid in uids:
        await check_dynamic(uid)


blive_config = Config.parse_obj(get_driver().config.dict())
dynamic_cron = blive_config.bilibili_dynamic_cron

scheduler.add_job(
    dynamic_monitor,
    "cron",
    second=dynamic_cron[0],
    minute=dynamic_cron[1],
    hour=dynamic_cron[2],
    day=dynamic_cron[3],
    month=dynamic_cron[4],
    year=dynamic_cron[5],
    id="bilibili_dynamic_cron",
)
