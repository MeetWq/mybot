from nonebot import export, on_command
from nonebot.typing import T_State
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

    if not keyword.isdigit() and keyword not in ['日榜', 'day', '周榜', 'week', '月榜', 'month', '月榜', 'month']:
        if not event.is_tome():
            await pixiv.finish()

    msg = await get_pixiv(keyword)
    if not str(msg):
        await pixiv.finish('出错了，请稍后再试')
    await pixiv.send(message=msg)
    await pixiv.finish()
