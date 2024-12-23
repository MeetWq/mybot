from nonebot import on_command, require
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from nonebot_plugin_alconna import Image, UniMessage
from nonebot_plugin_uninfo import Uninfo

from .data_source import get_tarot

__plugin_meta__ = PluginMetadata(
    name="塔罗牌",
    description="塔罗牌占卜",
    usage="单张塔罗牌",
)


tarot = on_command(
    "塔罗牌",
    aliases={"单张塔罗牌", "塔罗牌占卜", "draw 单张塔罗牌", "draw 塔罗牌"},
    block=True,
    priority=13,
)


@tarot.handle()
async def _(matcher: Matcher, session: Uninfo):
    username = session.user.nick or session.user.name or ""
    if session.member and session.member.nick:
        username = session.member.nick
    msg = UniMessage(f"来看看 {username} 抽到了什么：")
    try:
        img, meaning = await get_tarot()
    except Exception:
        await matcher.finish("出错了，请稍后再试")
    msg += Image(raw=img)
    msg += meaning
    await msg.send()
