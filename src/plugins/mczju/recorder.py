from datetime import datetime

from lxml import etree
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_orm import get_session

from .config import mczju_config
from .data_source import get_dynmap_update
from .model import MessageRecord

last_update: int = 0


@scheduler.scheduled_job(
    "interval",
    seconds=mczju_config.mczju_dynmap_update_interval,
    id="mczju_dynmap_update_schedule",
)
async def _():
    global last_update

    result = await get_dynmap_update()
    if not result:
        return

    updates = result["updates"]
    if not updates:
        return

    updates = [
        update
        for update in updates
        if update["type"] == "chat" and update["timestamp"] > last_update
    ]
    if not updates:
        return
    last_update = max(update["timestamp"] for update in updates)

    async with get_session() as db_session:
        for update in updates:
            time = datetime.fromtimestamp(update["timestamp"] / 1000)
            account = update["account"]
            if not account:
                account = (
                    etree.HTML(update["playerName"], etree.HTMLParser())
                    .xpath("string(.)")
                    .strip()
                )
            record = MessageRecord(
                time=time,
                account=account,
                message=update["message"],
            )
            db_session.add(record)
        await db_session.commit()
