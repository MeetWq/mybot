import re

from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_saa")

from nonebot_plugin_saa import Image, MessageFactory

from .config import Config
from .data_source import get_wolframalpha_simple, get_wolframalpha_text

__plugin_meta__ = PluginMetadata(
    name="WolframAlpha",
    description="WolframAlpha计算知识引擎",
    usage="wolfram {text}",
    config=Config,
    extra={
        "example": "wolfram int x",
    },
)


wolfram = on_command("wolfram", aliases={"wolframalpha"}, block=True, priority=12)


@wolfram.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()

    plaintext = False
    pattern = [r"-p +.*?", r".*? +-p", r"--plaintext +.*?", r".*? +--plaintext"]
    for p in pattern:
        if re.fullmatch(p, text):
            plaintext = True
            break
    text = text.replace("-p", "").replace("--plaintext", "").strip()
    if not text:
        await matcher.finish()

    if plaintext:
        res = await get_wolframalpha_text(text)
    else:
        res = await get_wolframalpha_simple(text)

    if not res:
        await matcher.finish("出错了，请稍后再试")

    if isinstance(res, str):
        await matcher.finish(res)
    else:
        await MessageFactory([Image(res)]).send()
