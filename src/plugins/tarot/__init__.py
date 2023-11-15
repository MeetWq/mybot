from nonebot import on_command, require
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_saa")
require("nonebot_plugin_userinfo")

from nonebot_plugin_saa import Image, MessageFactory
from nonebot_plugin_userinfo import EventUserInfo, UserInfo

from .data_source import get_tarot

__plugin_meta__ = PluginMetadata(
    name="塔罗牌",
    description="塔罗牌占卜",
    usage="单张塔罗牌",
)


tarot = on_command(
    "塔罗牌", aliases={"单张塔罗牌", "塔罗牌占卜", "draw 单张塔罗牌", "draw 塔罗牌"}, block=True, priority=13
)


@tarot.handle()
async def _(matcher: Matcher, userinfo: UserInfo = EventUserInfo()):
    username = userinfo.user_displayname or userinfo.user_name
    msg = MessageFactory(f"来看看 {username} 抽到了什么：")
    try:
        img, meaning = await get_tarot()
    except:
        await matcher.finish("出错了，请稍后再试")
    msg.append(Image(img))
    msg.append(meaning)
    await msg.send()
