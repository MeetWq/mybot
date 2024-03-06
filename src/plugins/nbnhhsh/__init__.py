import re

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .data_source import get_nbnhhsh

__plugin_meta__ = PluginMetadata(
    name="能不能好好说话",
    description="拼音首字母缩写翻译工具",
    usage="nbnhhsh/缩写 xxx",
    extra={
        "example": "缩写 xswl",
    },
)

nbnhhsh = on_command("nbnhhsh", aliases={"缩写"}, block=True, priority=13)


@nbnhhsh.handle()
async def _(msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        await nbnhhsh.finish()
    if not re.fullmatch(r"[a-zA-Z]+", keyword):
        await nbnhhsh.finish()

    res = await get_nbnhhsh(keyword)
    if res:
        await nbnhhsh.finish(res)
    else:
        await nbnhhsh.finish("找不到相关的缩写")
