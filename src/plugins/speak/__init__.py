from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .config import Config
from .data_source import get_voice

__plugin_meta__ = PluginMetadata(
    name="语音合成",
    description="文字转语音，支持中文/日文",
    usage="@我 说 {text}",
    config=Config,
    extra={
        "example": "@小Q 说你是猪",
    },
)


speak = on_command("speak", aliases={"说"}, block=True, rule=to_me(), priority=11)


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
