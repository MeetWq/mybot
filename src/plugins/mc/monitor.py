import re
from bs4 import BeautifulSoup
from nonebot import require, get_bots, get_driver

from .dynmap_source import get_dynmap_updates
from .dynmap_list import get_dynmap_list, dump_dynmap_list, set_last_update

from .config import Config
global_config = get_driver().config
mc_config = Config(**global_config.dict())


def user_type(user_id: str):
    p_group = r'group_(\d+)'
    p_private = r'private_(\d+)'
    match = re.fullmatch(p_group, user_id)
    if match:
        return 'group', match.group(1)
    match = re.fullmatch(p_private, user_id)
    if match:
        return 'private', match.group(1)
    return '', user_id


async def send_bot_msg(user_id: str, msg):
    type, id = user_type(user_id)
    bots = list(get_bots().values())
    for bot in bots:
        if type == 'group':
            await bot.send_group_msg(group_id=id, message=msg)
        elif type == 'private':
            await bot.send_private_msg(user_id=id, message=msg)


async def dynmap_monitor():
    dynmap_list = get_dynmap_list()
    for user_id, config in dynmap_list.items():
        if not config['chat']:
            continue

        url = config['update_url']
        result = await get_dynmap_updates(url)
        if not result:
            continue

        updates = result['updates']
        chats = []
        last_update = config['last_update']
        for update in updates:
            if update['timestamp'] > last_update:
                last_update = update['timestamp']
            if update['type'] != 'chat':
                continue
            if update['timestamp'] <= config['last_update']:
                continue
            chats.append(update)
        set_last_update(user_id, last_update)
        if not chats:
            continue

        msgs = []
        for chat in chats:
            name = chat['playerName']
            name = BeautifulSoup(name).text
            message = chat['message']
            msgs.append(f'[dynmap] {name}: {message}')
        msg = '\n'.join(msgs)
        await send_bot_msg(user_id, msg)
    dump_dynmap_list()


scheduler = require("nonebot_plugin_apscheduler").scheduler
dynmap_cron = mc_config.dynmap_cron


scheduler.add_job(
    dynmap_monitor,
    'cron',
    second=dynmap_cron[0],
    minute=dynmap_cron[1],
    hour=dynmap_cron[2],
    day=dynmap_cron[3],
    month=dynmap_cron[4],
    year=dynmap_cron[5],
    id='dynmap_monitor',
    coalesce=True,
    misfire_grace_time=30
)
