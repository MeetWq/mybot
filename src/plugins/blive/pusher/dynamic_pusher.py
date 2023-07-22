from typing import Dict

from bilireq.exceptions import GrpcError
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType
from grpc import StatusCode
from grpc.aio import AioRpcError
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Image, MessageFactory

from ..config import blive_config
from ..database.db import get_dynamic_targets, get_dynamic_uids, update_user
from ..models import BiliUser
from ..utils import get_dynamic_screenshot

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
        dynamics = (await grpc_get_user_dynamics(int(uid), timeout=30)).list
    except AioRpcError as e:
        if e.code() == StatusCode.DEADLINE_EXCEEDED:
            logger.warning(f"爬取动态超时，将在下个轮询中重试：{e.code()} {e.details()}")
        else:
            logger.warning(f"爬取动态失败：{e.code()} {e.details()}")
        return
    except GrpcError as e:
        logger.warning(f"爬取动态失败：{e.code} {e.msg}")
        return

    if uid not in dynamic_offset:
        if not dynamics:
            dynamic_offset[uid] = 0
        elif len(dynamics) == 1:
            dynamic_offset[uid] = int(dynamics[0].extend.dyn_id_str)
        else:
            dynamic_offset[uid] = max(
                int(dynamics[0].extend.dyn_id_str), int(dynamics[1].extend.dyn_id_str)
            )
        return

    if not dynamics:
        return

    name = dynamics[0].modules[0].module_author.author.name

    dynamic = None
    for dynamic in sorted(dynamics, key=lambda x: int(x.extend.dyn_id_str)):
        dynamic_id = int(dynamic.extend.dyn_id_str)
        if dynamic_id > dynamic_offset[uid]:
            logger.info(f"检测到新动态：{dynamic_id}")
            dynamic_offset[uid] = dynamic_id

            if dynamic.card_type in [
                DynamicType.live_rcmd,
                DynamicType.live,
                DynamicType.ad,
                DynamicType.banner,
            ]:
                logger.info(f"无需推送的动态 {dynamic.card_type}，已跳过：{dynamic_id}")
                return

            if not (image := await get_dynamic_screenshot(dynamic_id)):
                logger.warning(f"获取动态截图失败：{dynamic_id}")
                return

            type_msg = {
                0: "发布了新动态",
                DynamicType.forward: "转发了一条动态",
                DynamicType.word: "发布了新文字动态",
                DynamicType.draw: "发布了新图文动态",
                DynamicType.av: "发布了新投稿",
                DynamicType.article: "发布了新专栏",
                DynamicType.music: "发布了新音频",
            }
            msg = MessageFactory([])
            msg.append(f"{name} {type_msg.get(dynamic.card_type, type_msg[0])}：\n")
            msg.append(Image(image))
            msg.append(f"https://t.bilibili.com/{dynamic_id}")

            targets = await get_dynamic_targets(uid)
            for target in targets:
                try:
                    await msg.send_to(target)
                except Exception as e:
                    logger.warning(f"Error in sending dynamic message to {target}: {e}")
                    continue

    if dynamic:
        await update_user(BiliUser(uid=uid, name=name))
