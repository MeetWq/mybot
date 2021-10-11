from nonebot import export, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_response

export = export()
export.description = 'NHD娘'
export.usage = 'Usage:\n  NHD娘，{xxx}'
export.help = export.description + '\n' + export.usage

nhdgirl = on_regex(r'^[Nn][Hh][Dd]娘', priority=33)


@nhdgirl.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.get_plaintext().strip().lower().replace('nhd娘', '')
    if msg:
        nickname = event.sender.card or event.sender.nickname
        reply = await get_response(msg, nickname)
        if reply:
            nhdgirl.block = True
            await nhdgirl.finish(reply)
    nhdgirl.block = False
    await nhdgirl.finish()
