import nonebot
from typing import Union
from nonebot.log import logger

from .models import (
    LiveBeganEvent,
    LiveEndedEvent,
    RecordingStartedEvent,
    ErrorEvent,
    UploaderEvent,
    LiveInfo,
)
from .send_msg import send_live_msg, send_record_msg, send_superuser_msg
from .uid_list import get_sub_info_by_uid, get_sub_info_by_roomid

app = nonebot.get_app()


@app.post("/blive/blrec")
async def blrec_handler(
    event: Union[LiveBeganEvent, LiveEndedEvent, RecordingStartedEvent]
):
    logger.info(str(event))
    if isinstance(event, RecordingStartedEvent):
        uid = str(event.data.room_info.uid)
        info = get_sub_info_by_uid(str(uid))
        if info:
            await send_record_msg(uid, f"{info['up_name']} 录播启动...")
    else:
        user_info = event.data.user_info
        room_info = event.data.room_info
        live_info = LiveInfo(user_info, room_info)
        live_msg = await live_info.format_msg()
        if live_msg:
            uid = str(event.data.user_info.uid)
            await send_live_msg(uid, live_msg)


@app.post("/blive/blrec/error")
async def blrec_error_handler(event: ErrorEvent):
    logger.info(str(event))
    await send_superuser_msg(f"blrec error: {event.data.detail}")


@app.post("/blive/uploader")
async def uploader_handler(event: UploaderEvent):
    logger.info(str(event))
    if event.data.err_msg:
        await send_superuser_msg(f"uploader error: {event.data.err_msg}")
    elif event.data.share_url:
        room_id = event.data.room_id
        info = get_sub_info_by_roomid(room_id)
        if info:
            await send_record_msg(
                info["uid"], f"{info['up_name']} 的录播文件：\n{event.data.share_url}"
            )
