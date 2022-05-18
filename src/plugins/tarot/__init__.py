from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment

from .data_source import get_tarot


__des__ = "塔罗牌占卜"
__cmd__ = """
单张塔罗牌
""".strip()
__short_cmd__ = __cmd__
__usage__ = f"{__des__}\nUsage:\n{__cmd__}"


tarot = on_command("塔罗牌", aliases={"单张塔罗牌", "塔罗牌占卜", "draw 单张塔罗牌", "draw 塔罗牌"}, block=True, priority=13)


@tarot.handle()
async def _(event: MessageEvent):
    username = event.sender.card or event.sender.nickname
    message = Message(f"来看看 {username} 抽到了什么：")
    try:
        img, meaning = await get_tarot()
    except:
        await tarot.finish("出错了，请稍后再试")
    message.append(MessageSegment.image(img))
    message.append(meaning)
    await tarot.finish(message)
