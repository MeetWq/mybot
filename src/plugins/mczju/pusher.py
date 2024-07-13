from datetime import datetime

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_orm import get_session
from nonebot_plugin_saa import Text
from sqlalchemy import select

from .config import dynmap_targets, mczju_config
from .model import MessageRecord

last_update: datetime = datetime.now()


@scheduler.scheduled_job(
    "interval",
    seconds=mczju_config.mczju_dynmap_send_interval,
    id="mczju_dynmap_send_schedule",
)
async def _():
    global last_update
    statement = select(MessageRecord).where(MessageRecord.time > last_update)
    async with get_session() as db_session:
        records = (await db_session.scalars(statement)).all()
    if not records:
        return
    last_update = max(record.time for record in records)

    msgs = []
    for record in records:
        msgs.append(f"[dynmap] {record.account}: {record.message}")
    msg = "\n".join(msgs)

    for target in dynmap_targets:
        try:
            await Text(msg).send_to(target)
        except Exception as e:
            logger.warning(f"Error sending msg '{msg}' to target '{target}': {e}")
