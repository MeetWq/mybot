import asyncio
from typing import Type
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment

from .data_source import get_setu


__plugin_meta__ = PluginMetadata(
    name="涩图",
    description="随机涩图",
    usage="@我 setu [keyword]",
    extra={
        "example": "@小Q setu 伊蕾娜",
    },
)


setu = on_command("setu", aliases={"涩图", "色图"}, rule=to_me(), block=True, priority=14)
setu_ = on_command("r18", permission=SUPERUSER, rule=to_me(), block=True, priority=14)


@setu.handle()
async def _(bot: Bot, msg: Message = CommandArg()):
    await handle(bot, setu, msg)


@setu_.handle()
async def _(bot: Bot, msg: Message = CommandArg()):
    await handle(bot, setu_, msg, r18=True)


async def handle(bot: Bot, matcher: Type[Matcher], msg: Message, r18=False):
    keyword = msg.extract_plain_text().strip()
    res = await get_setu(keyword=keyword, r18=r18)
    if not res:
        await matcher.finish("出错了，请稍后再试")
    if isinstance(res, str):
        await matcher.finish(res)
    else:
        result = await matcher.send(MessageSegment.image(res))
        msg_id = result["message_id"]
        loop = asyncio.get_running_loop()
        loop.call_later(
            100, lambda: asyncio.ensure_future(bot.delete_msg(message_id=msg_id))
        )
