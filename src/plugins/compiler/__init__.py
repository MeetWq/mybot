import re

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .data_source import legal_language, network_compile

language = ", ".join(list(legal_language.keys()))

__plugin_meta__ = PluginMetadata(
    name="网络编译器",
    description="在线运行代码",
    usage=f"lang {{language}};\n{{code}}\n\n支持的语言：{language}",
    extra={
        "example": "lang py3;\nprint('hello')",
        "notice": "来源为菜鸟教程的网络编译器，不要试图搞事情",
    },
)

compiler = on_command("lang", force_whitespace=True, block=True, priority=13)


@compiler.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    text = msg.extract_plain_text().lstrip()
    if not text:
        await matcher.finish()
    matched = re.match(r"^(?P<language>[^;；\s]+)[;；\s]+(?P<code>[^;；\s]+.*)", text)
    if not matched:
        await matcher.finish()

    args = matched.groupdict()
    language = str(args["language"]).strip()
    code = str(args["code"]).strip()
    if language not in legal_language:
        await matcher.finish(f"支持的语言：{language}")

    result = await network_compile(language, code)
    if not result:
        await matcher.finish("出错了，请稍后再试")
    else:
        await matcher.finish(result["output"] if result["output"] else result["errors"])
