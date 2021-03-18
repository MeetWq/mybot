from nonebot import get_driver, on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, PrivateMessageEvent

from .data_source import get_pixiv
from .config import Config

global_config = get_driver().config
pixiv_config = Config(**global_config.dict())

pixiv = on_command('pixiv', priority=17)


@pixiv.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = str(event.get_message()).strip()
    if not keyword:
        await pixiv.finish('使用方法：pixiv + "日榜/周榜/年榜/作品id/关键词"')
    if keyword in ['日榜', 'day', '周榜', 'week', '月榜', 'month']:
        await pixiv.send('请稍候，将随机发送3张图片')
    else:
        await pixiv.send('请稍候...')
    
    r18 = False
    if isinstance(event, PrivateMessageEvent) or str(event.group_id) in pixiv_config.pixiv_group:
        r18 = True
    msg = await get_pixiv(keyword, r18)

    if not str(msg):
        await pixiv.finish('出错了，请稍后再试')
    await pixiv.send(message=msg)
    await pixiv.finish()
