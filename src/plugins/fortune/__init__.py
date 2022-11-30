import traceback
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.log import logger

from .config import Config
from .data_source import get_fortune


__plugin_meta__ = PluginMetadata(
    name="运势",
    description="测试你的今日运势",
    usage="今日运势/今日人品/jrrp",
    config=Config,
)


jrrp = on_command("jrrp", aliases={"今日运势", "今日人品"}, block=True, priority=13)


@jrrp.handle()
async def _(event: MessageEvent):
    user_id = event.user_id
    username = event.sender.card or event.sender.nickname or ""

    res = None
    try:
        res = await get_fortune(user_id, username)
    except:
        logger.warning(traceback.format_exc())

    if not res:
        await jrrp.finish("出错了，请稍后再试")

    await jrrp.finish(MessageSegment.image(res))
