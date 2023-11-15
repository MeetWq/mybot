import traceback

from nonebot import on_command, require
from nonebot.adapters import Event
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_saa")
require("nonebot_plugin_userinfo")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_saa import Image, MessageFactory
from nonebot_plugin_userinfo import EventUserInfo, UserInfo

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
async def _(matcher: Matcher, event: Event, userinfo: UserInfo = EventUserInfo()):
    user_id = event.get_user_id()
    username = userinfo.user_displayname or userinfo.user_name

    res = None
    try:
        res = await get_fortune(user_id, username)
    except:
        logger.warning(traceback.format_exc())

    if not res:
        await matcher.finish("出错了，请稍后再试")

    await MessageFactory([Image(res)]).send()
