import nonebot
from typing import Union
from cachetools import TTLCache
from nonebot.log import logger

from .models import (
    LiveBeganEvent,
    LiveEndedEvent,
    RecordingStartedEvent,
    ErrorEvent,
    UploaderEvent,
    LiveInfo,
)
from .send_msg import send_live_msg, send_record_msg, send_superuser_msg, send_bot_msg
from .uid_list import get_sub_info_by_uid, get_sub_info_by_roomid
from .blrec import get_task
from .models import LiveStatus

app = nonebot.get_app()


uid_cache = TTLCache(maxsize=100, ttl=60 * 5)


@app.post("/blive/blrec")
async def blrec_handler(
    event: Union[LiveBeganEvent, LiveEndedEvent, RecordingStartedEvent]
):
    logger.info(str(event))
    room_info = event.data.room_info
    uid = str(room_info.uid)

    if isinstance(event, RecordingStartedEvent):

        key = f"{uid}_record"
        if key in uid_cache:
            logger.warning(f"skip send msg for {key}")
            return

        info = get_sub_info_by_uid(uid)
        if info:
            await send_record_msg(uid, f"{info['up_name']} 录播启动...")
            uid_cache[key] = True
    else:

        key = f"{uid}_live"
        if key in uid_cache:
            logger.warning(f"skip send msg for {key}")
            return

        user_info = event.data.user_info
        live_info = LiveInfo(user_info, room_info)
        live_msg = await live_info.format_msg()
        if live_msg:
            await send_live_msg(uid, live_msg)
            uid_cache[key] = True


@app.post("/blive/blrec/error")
async def blrec_error_handler(event: ErrorEvent):
    logger.info(str(event))
    await send_superuser_msg(f"blrec error: {event.data.detail}")


@app.post("/blive/uploader")
async def uploader_handler(event: UploaderEvent):
    logger.info(str(event))
    if event.data.err_msg:
        await send_superuser_msg(f"uploader error: {event.data.err_msg}")
        return

    if not event.data.share_url:
        return

    room_id = str(event.data.room_id)
    info = get_sub_info_by_roomid(room_id)
    if not info:
        return
    user_id = event.id
    if user_id.startswith("private") or user_id.startswith("group"):
        await send_bot_msg(user_id, f"{info['up_name']} 的切片文件：\n{event.data.share_url}")
    else:
        task_info = await get_task(room_id)
        if task_info and task_info.room_info.live_status == LiveStatus.LIVE:
            logger.info("当前直播尚未结束，取消发送录播文件链接")
            return
        await send_record_msg(
            info["uid"], f"{info['up_name']} 的录播文件：\n{event.data.share_url}"
        )
