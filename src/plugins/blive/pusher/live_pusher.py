import time
from typing import Dict

from bilireq.live import get_rooms_info_by_uids
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Image, MessageFactory

from ..config import blive_config
from ..database.db import get_live_targets, get_live_uids, update_user
from ..models import BiliUser

live_status: Dict[int, int] = {}


def is_live(status: int) -> bool:
    return status == 1


@scheduler.scheduled_job(
    "interval", seconds=blive_config.blive_live_interval, id="blive_live_schedule"
)
async def _():
    uids = await get_live_uids()
    if not uids:
        return

    res = await get_rooms_info_by_uids(list(uids))
    if not res:
        return

    for uid_str, info in res.items():
        status = info["live_status"]
        uid = int(uid_str)
        if uid_str not in live_status:
            live_status[uid] = status
            continue

        if is_live(live_status[uid]) == is_live(status):
            continue

        live_status[uid] = status
        logger.info(f"User {uid} live status changed to {status}")

        msg = MessageFactory([])
        name = info["uname"]
        room_id = info["short_id"] or info["room_id"]

        if status == 1:
            live_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(info["live_time"])
            )
            title = info["title"]
            url = f"https://live.bilibili.com/{room_id}"
            cover = info["cover_from_user"] or info["keyframe"]
            msg.append(f"{live_time}\n{name} 开播啦！\n{title}\n")
            msg.append(Image(cover))
            msg.append(f"{url}")

        elif status == 0:
            msg.append(f"{name} 下播了")

        elif status == 2:
            msg.append(f"{name} 下播了（轮播中）")

        targets = await get_live_targets(uid)
        for target in targets:
            try:
                await msg.send_to(target)
            except Exception as e:
                logger.warning(f"Error in sending live message to {target}: {e}")
                continue

        await update_user(BiliUser(uid=uid, name=name, room_id=room_id))
