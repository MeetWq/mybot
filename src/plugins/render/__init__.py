from nonebot.params import CommandArg
from nonebot import on_command, require
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .data_source import t2p, m2p

require("nonebot_plugin_htmlrender")

__plugin_meta__ = PluginMetadata(
    name="文本渲染",
    description="文本、Markdown转图片",
    usage="text2pic/t2p {text}\nmd2pic/m2p {text}",
    extra={
        "example": "t2p test\nm2p $test$ test `test`",
    },
)


text2pic = on_command("text2pic", aliases={"t2p"}, block=True, priority=12)
md2pic = on_command("md2pic", aliases={"markdown", "m2p"}, block=True, priority=12)


@text2pic.handle()
async def _(msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()
    if not text:
        await text2pic.finish()

    img = await t2p(text)
    if img:
        await text2pic.finish(MessageSegment.image(img))


@md2pic.handle()
async def _(msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()
    if not text:
        await md2pic.finish()

    img = await m2p(text)
    if img:
        await md2pic.finish(MessageSegment.image(img))
