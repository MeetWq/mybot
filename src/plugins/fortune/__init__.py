from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent

from .data_source import get_response

export = export()
export.description = '今日运势'
export.usage = 'Usage:\n  今日运势/今日人品/抽签'
export.help = export.description + '\n' + export.usage

jrrp = on_command('jrrp', aliases={'今日运势', '今日人品', '抽签'}, priority=32)


@jrrp.handle()
async def _(bot: Bot, event: Event, state: T_State):
    user_id = event.user_id
    username = event.sender.card or event.sender.nickname
    group_id = 0
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
    reponse = await get_response(group_id, user_id, username)
    await jrrp.send(message=reponse)
    await jrrp.finish()
