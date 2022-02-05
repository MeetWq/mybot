import nonebot
from typing import Union

from .models import (
    LiveBeganEvent,
    LiveEndedEvent,
    ErrorEvent,
    UploaderEvent,
    LiveInfo,
)
from .send_msg import send_live_msg, send_record_msg, send_superuser_msg
from .uid_list import get_sub_info_by_roomid

app = nonebot.get_asgi()


@app.post("/blive/blrec")
async def blrec_handler(event: Union[LiveBeganEvent, LiveEndedEvent]):
    user_info = event.data.user_info
    room_info = event.data.room_info
    live_info = LiveInfo(user_info, room_info)
    live_msg = await live_info.format_msg()
    uid = str(event.data.user_info.uid)
    up_name = event.data.user_info.name
    await send_live_msg(uid, live_msg)
    await send_record_msg(uid, f"{up_name} 录播启动...")


@app.post("/blive/blrec/error")
async def blrec_error_handler(event: ErrorEvent):
    await send_superuser_msg(f"blrec error: {event.data.detail}")


@app.post("/blive/uploader")
async def uploader_handler(event: UploaderEvent):
    if event.data.err_msg:
        await send_superuser_msg(f"uploader error: {event.data.err_msg}")
    elif event.data.share_url:
        room_id = event.data.room_id
        info = get_sub_info_by_roomid(room_id)
        if info:
            await send_record_msg(
                info['uid'], f"{info['up_name']} 的录播文件：\n{event.data.share_url}"
            )
