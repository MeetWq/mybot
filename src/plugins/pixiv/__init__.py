from nonebot import export, on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event, PrivateMessageEvent

from .data_source import get_pixiv
from .config import Config

export = export()
export.description = 'Pixiv图片'
export.usage = 'Usage:\n  pixiv {日榜/周榜/年榜/id}'
export.notice = 'Notice:\n  已加入图片内容检测功能，不合适的图片会被替换'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

pixiv = on_command('pixiv', priority=17)
pixiv_ = on_command('pixiv_', permission=SUPERUSER, priority=21)

@pixiv.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()

    if keyword in ['日榜', 'day', '周榜', 'week', '月榜', 'month']:
        await pixiv.send('请稍候，将随机发送3张图片')
    elif keyword.isdigit():
        await pixiv.send('请稍候...')
    else:
        await pixiv.finish(export.usage)

    msg = await get_pixiv(keyword)
    if not str(msg):
        await pixiv.finish('出错了，请稍后再试')
    await pixiv.send(message=msg)
    await pixiv.finish()


@pixiv_.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    if not keyword:
        pixiv_.finish(export.usage)

    await pixiv_.send('请稍候...')
    msg = await get_pixiv(keyword, True)
    if not str(msg):
        await pixiv_.finish('出错了，请稍后再试')
    await pixiv_.send(message=msg)
    await pixiv_.finish()
