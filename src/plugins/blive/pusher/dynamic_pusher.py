import traceback
from typing import Dict

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Image, MessageFactory

from ..config import blive_config
from ..database.db import get_dynamic_targets, get_dynamic_uids, update_user
from ..models import BiliUser
from ..utils import get_dynamic_screenshot, get_user_dynamics

dynamic_offset: Dict[str, int] = {}
updated_uids = set()


def next_uid(uids) -> str:
    for uid in uids:
        if uid not in updated_uids:
            updated_uids.add(uid)
            return uid
    updated_uids.clear()
    return next_uid(uids)


@scheduler.scheduled_job(
    "interval", seconds=blive_config.blive_dynamic_interval, id="blive_dynamic_schedule"
)
async def _():
    uids = await get_dynamic_uids()
    if not uids:
        return

    uid = next_uid(uids)

    try:
        dynamics = (await get_user_dynamics(int(uid)))["items"]
    except:
        logger.warning(f"爬取动态失败：{uid}\n{traceback.format_exc()}")
        return

    if not dynamics:
        return

    if uid not in dynamic_offset:
        dynamic_offset[uid] = max([int(dynamic["id_str"]) for dynamic in dynamics])
        return

    dynamics = [
        dynamic for dynamic in dynamics if int(dynamic["id_str"]) > dynamic_offset[uid]
    ]
    if not dynamics:
        return

    name = dynamics[0]["modules"]["module_author"]["name"]
    for dynamic in sorted(dynamics, key=lambda x: int(x["id_str"])):
        dynamic_id = int(dynamic["id_str"])
        dyn_type = dynamic["type"]
        logger.info(f"检测到新动态：{dynamic_id}")
        dynamic_offset[uid] = dynamic_id

        if dyn_type in [
            "DYNAMIC_TYPE_LIVE_RCMD",
            "DYNAMIC_TYPE_LIVE",
            "DYNAMIC_TYPE_AD",
            "DYNAMIC_TYPE_BANNER",
        ]:
            logger.info(f"无需推送的动态 {dyn_type}，已跳过：{dynamic_id}")
            return

        if not (image := await get_dynamic_screenshot(dynamic_id)):
            logger.warning(f"获取动态截图失败：{dynamic_id}")
            return

        type_msg = {
            "DYNAMIC_TYPE_FORWARD": "转发了一条动态",
            "DYNAMIC_TYPE_WORD": "发布了新文字动态",
            "DYNAMIC_TYPE_DRAW": "发布了新图文动态",
            "DYNAMIC_TYPE_AV": "发布了新投稿",
            "DYNAMIC_TYPE_ARTICLE": "发布了新专栏",
            "DYNAMIC_TYPE_MUSIC": "发布了新音频",
        }
        text = type_msg.get(dyn_type, "发布了新动态")
        msg = MessageFactory([])
        msg.append(f"{name} {text}：\n")
        msg.append(Image(image))
        msg.append(f"https://t.bilibili.com/{dynamic_id}")

        targets = await get_dynamic_targets(uid)
        for target in targets:
            try:
                await msg.send_to(target)
            except Exception as e:
                logger.warning(f"Error in sending dynamic message to {target}: {e}")
                continue

    await update_user(BiliUser(uid=uid, name=name))
