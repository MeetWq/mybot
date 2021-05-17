from nonebot import export, on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_pixiv

export = export()
export.description = 'Pixiv图片'
export.usage = 'Usage:\n  pixiv {日榜/周榜/月榜/id/关键词}'
export.help = export.description + '\n' + export.usage

pixiv = on_command('pixiv', priority=25)


@pixiv.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    if not keyword:
        await pixiv.finish(export.usage)

    msg = await get_pixiv(keyword)
    if not str(msg):
        await pixiv.finish('出错了，请稍后再试')
    await pixiv.send(message=msg)
    await pixiv.finish()
