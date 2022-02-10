import re
from nonebot import get_bot, get_driver
from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_apscheduler import scheduler

from .data_source import update_rss
from .render import rss_to_msg
from .rss_list import get_rss_list, get_user_ids, dump_rss_list

from .config import Config

rss_config = Config.parse_obj(get_driver().config.dict())


def user_type(user_id: str):
    p_group = r"group_(\d+)"
    p_private = r"private_(\d+)"
    match = re.fullmatch(p_group, user_id)
    if match:
        return "group", match.group(1)
    match = re.fullmatch(p_private, user_id)
    if match:
        return "private", match.group(1)
    return "", user_id


async def rss_monitor():
    bot = get_bot()
    assert isinstance(bot, Bot)
    user_ids = get_user_ids()
    for user_id in user_ids:
        user_rss_list = get_rss_list(user_id)
        for rss in user_rss_list:
            entries = await update_rss(rss)
            for entry in entries:
                msg = await rss_to_msg(rss, entry)
                if not msg:
                    continue
                type, id = user_type(user_id)
                if type == "group":
                    await bot.send_group_msg(group_id=int(id), message=msg)
                elif type == "private":
                    await bot.send_private_msg(user_id=int(id), message=msg)
    dump_rss_list()


rss_cron = rss_config.rss_update_cron
scheduler.add_job(
    rss_monitor,
    "cron",
    second=rss_cron[0],
    minute=rss_cron[1],
    hour=rss_cron[2],
    day=rss_cron[3],
    month=rss_cron[4],
    year=rss_cron[5],
    id="rss_monitor",
    coalesce=True,
    misfire_grace_time=30,
)
