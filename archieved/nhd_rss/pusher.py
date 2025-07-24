from datetime import datetime, timedelta, timezone

from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Image, MessageFactory, PlatformTarget

from .config import rss_config
from .data_source import get_rss_entries
from .render import rss_to_image

targets = [PlatformTarget.deserialize(target) for target in rss_config.nhd_rss_targets]
last_update: datetime = datetime.now().astimezone(timezone(timedelta(hours=8)))


@scheduler.scheduled_job(
    "interval", seconds=rss_config.nhd_rss_interval, id="nhd_rss_schedule"
)
async def _():
    entries = await get_rss_entries()
    entries = sorted(entries, key=lambda x: x.pubDate)
    entries = [e for e in entries if e.pubDate > last_update]
    if not entries:
        return
    global last_update
    last_update = entries[-1].pubDate

    for entry in entries:
        image = await rss_to_image(entry)
        if not image:
            continue
        msg = MessageFactory([Image(image)])
        for target in targets:
            try:
                await msg.send_to(target)
            except Exception as e:
                logger.warning(f"Error sending msg '{msg}' to target '{target}': {e}")
