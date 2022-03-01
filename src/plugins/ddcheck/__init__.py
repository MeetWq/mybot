from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .data_source import get_reply


__des__ = "成分姬"
__cmd__ = """
查成分 {用户名/UID}
""".strip()
__short_cmd__ = __cmd__
__example__ = """
查成分 小南莓Official
""".strip()
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"


ddcheck = on_command("查成分", block=True, priority=12)


@ddcheck.handle()
async def _(msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()
    if not text:
        await ddcheck.finish()

    res = await get_reply(text)
    if not res:
        await ddcheck.finish("出错了，请稍后再试")
    elif isinstance(res, str):
        await ddcheck.finish(res)
    else:
        await ddcheck.finish(MessageSegment.image(res))
