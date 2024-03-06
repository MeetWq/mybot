from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import UniMessage

from .data_source import tex2pic

__plugin_meta__ = PluginMetadata(
    name="LaTeX公式",
    description="支持行内公式和少量行间公式",
    usage="tex {equation}",
    extra={
        "example": (
            "tex a + b = c\ntex \\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}"
        ),
    },
)


tex = on_command("tex", block=True, priority=12)


@tex.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    equation = msg.extract_plain_text().strip().strip("$")
    if not equation:
        await matcher.finish()

    image = await tex2pic(equation)
    if image:
        await UniMessage.image(raw=image).send()
    else:
        await matcher.finish("出错了，请检查公式或稍后再试")
