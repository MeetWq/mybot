import nonebot
from cachetools import TTLCache
from nonebot.log import logger
from nonebot_plugin_saa import MessageFactory

from ..database.db import get_record_targets, get_user, get_users
from .models import ErrorEvent, LiveStatus, RecordingStartedEvent, UploaderEvent
from .task import get_task, sync_tasks

app = nonebot.get_app()


uid_cache = TTLCache(maxsize=100, ttl=60 * 5)


@app.post("/blive/blrec")
async def blrec_handler(event: RecordingStartedEvent):
    logger.info(str(event))
    room_info = event.data.room_info
    uid = str(room_info.uid)

    if uid in uid_cache:
        logger.warning(f"skip send msg for {uid}")
        return

    if not (user := await get_user(uid)):
        await sync_tasks()
        return

    msg = MessageFactory(f"{user.name} 录播启动...")
    uid_cache[uid] = True
    for target in await get_record_targets(uid):
        await msg.send_to(target)


@app.post("/blive/blrec/error")
async def blrec_error_handler(event: ErrorEvent):
    logger.warning(f"blrec error: {event}")


@app.post("/blive/uploader")
async def uploader_handler(event: UploaderEvent):
    logger.info(str(event))

    if event.data.err_msg:
        return
    if not event.data.share_url:
        return

    room_id = str(event.data.room_id)
    users = await get_users()
    for user in users:
        if user.room_id == room_id:
            task_info = await get_task(room_id)
            if task_info and task_info.room_info.live_status == LiveStatus.LIVE:
                logger.info("当前直播尚未结束，取消发送录播文件链接")
                return

            msg = MessageFactory(f"{user.name} 的录播文件：\n{event.data.share_url}")
            for target in await get_record_targets(user.uid):
                await msg.send_to(target)
            return
    await sync_tasks()
