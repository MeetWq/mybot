from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .data_source import get_voice


speak = on_command("说", block=True, rule=to_me(), priority=10)


@speak.handle()
async def _(msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()
    if not text:
        await speak.finish()

    voice = await get_voice(text)
    if voice:
        await speak.finish(MessageSegment.record(voice))
    else:
        await speak.finish("出错了，请稍后再试")
