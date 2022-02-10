from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment

from .data_source import get_fortune


__des__ = "今日运势"
__cmd__ = "今日运势/今日人品/jrrp"
__short_cmd__ = __cmd__
__usage__ = f"{__des__}\nUsage:\n{__cmd__}"


jrrp = on_command("jrrp", aliases={"今日运势", "今日人品"}, block=True, priority=13)


@jrrp.handle()
async def _(event: MessageEvent):
    user_id = event.user_id
    username = event.sender.card or event.sender.nickname
    res = await get_fortune(str(user_id), username)
    if not res:
        await jrrp.finish("出错了，请稍后再试")
    if isinstance(res, str):
        await jrrp.finish(res)
    else:
        await jrrp.finish(MessageSegment.image(res))
