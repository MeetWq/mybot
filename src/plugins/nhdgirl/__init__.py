from nonebot import export, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, GroupMessageEvent

from .data_source import get_reply

export = export()
export.description = 'NHD娘'
export.usage = 'Usage:\n  NHD娘，{xxx}'
export.help = export.description + '\n' + export.usage

nhdgirl = on_regex(r'^[Nn][Hh][Dd]娘', priority=33)


@nhdgirl.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip().lower().replace('nhd娘', '')
    reply = await get_reply(msg, event)
    if reply:
        await nhdgirl.send(message=reply)
        await nhdgirl.finish()
