from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_steam_game

export = export()
export.description = 'Steam游戏查询'
export.usage = 'Usage:\n  steam {keyword}'
export.help = export.description + '\n' + export.usage

steam = on_command('steam', priority=22)


@steam.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    if not keyword:
        await steam.finish(export.usage)

    msg = await get_steam_game(keyword)
    if not msg:
        await steam.finish('出错了，请稍后再试')

    await steam.send(message=msg)
    await steam.finish()
