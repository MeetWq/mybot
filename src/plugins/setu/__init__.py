from typing import Type
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .data_source import get_setu


__des__ = "随机涩图"
__cmd__ = """
@我 setu [keyword]
""".strip()
__short_cmd__ = __cmd__
__example__ = """
@小Q setu 伊蕾娜
""".strip()
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"


setu = on_command("setu", aliases={"涩图", "色图"}, rule=to_me(), block=True, priority=14)
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
        await matcher.finish(MessageSegment.image(res))
