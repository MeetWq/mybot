from typing import Type

from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import UniMessage

from .data_source import get_setu

__plugin_meta__ = PluginMetadata(
    name="涩图",
    description="随机涩图",
    usage="@我 setu {keyword}",
    extra={
        "example": "@小Q setu 小萝莉",
    },
)


setu = on_command(
    "setu", aliases={"涩图", "色图"}, rule=to_me(), block=True, priority=14
)
setu_ = on_command("r18", permission=SUPERUSER, rule=to_me(), block=True, priority=14)


@setu.handle()
async def _(msg: Message = CommandArg()):
    await handle(setu, msg)


@setu_.handle()
async def _(msg: Message = CommandArg()):
    await handle(setu_, msg, r18=True)


async def handle(matcher: Type[Matcher], msg: Message, r18=False):
    keyword = msg.extract_plain_text().strip()
    res = await get_setu(keyword=keyword, r18=r18)
    if not res:
        await matcher.finish("出错了，请稍后再试")
    if isinstance(res, str):
        await matcher.finish(res)
    else:
        await UniMessage.image(raw=res).send()
