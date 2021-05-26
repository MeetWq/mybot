from nonebot import export, require, get_bots

from .data_source import get_msgs

export = export()
export.description = 'PT风向旗'
export.usage = '转发PT风向旗的相关新闻'
export.help = export.description + '\n' + export.usage


async def update_ptfxq():
    msgs = await get_msgs()
    if not msgs:
        return

    bots = list(get_bots().values())
    for bot in bots:
        noitce_groups = []
        npm = require('nonebot_plugin_manager')
        group_list = await bot.get_group_list()
        for group in group_list:
            group_id = group['group_id']
            group_plugin_list = npm.get_group_plugin_list(str(group_id))
            if group_plugin_list['ptfxq']:
                noitce_groups.append(group_id)

        for group_id in noitce_groups:
            for msg in msgs:
                await bot.send_group_msg(group_id=group_id, message=msg)


scheduler = require('nonebot_plugin_apscheduler').scheduler

scheduler.add_job(
    update_ptfxq,
    'cron',
    hour='8-23',
    minute='*/20',
    id='ptfxq_in_day',
    coalesce=True,
    misfire_grace_time=30
)

scheduler.add_job(
    update_ptfxq,
    'cron',
    hour='0-7',
    minute='30',
    id='ptfxq_in_night',
    coalesce=True,
    misfire_grace_time=30
)
