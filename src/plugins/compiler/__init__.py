import re
from nonebot import on_regex
from nonebot.params import RegexDict
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import unescape

from .data_source import legal_language, network_compile


__plugin_meta__ = PluginMetadata(
    name="网络编译器",
    description="在线运行代码",
    usage=f"lang {{language}};\n{{code}}\n\n支持的语言：{', '.join(list(legal_language.keys()))}",
    extra={
        "example": "lang py3;\nprint('hello')",
        "notice": "来源为菜鸟教程的网络编译器，不要试图搞事情",
    },
)


compiler = on_regex(
    r"^lang\s+(?P<language>[^;；\s]+)[;；\s]+(?P<code>[^;；\s]+.*)",
    flags=re.S,
    block=True,
    priority=13,
)


@compiler.handle()
async def _(msg: dict = RegexDict()):
    language = str(msg["language"]).strip()
    code = unescape(unescape(str(msg["code"]))).strip()
    if language not in legal_language:
        await compiler.finish(f"支持的语言：{', '.join(list(legal_language.keys()))}")

    result = await network_compile(language, code)
    if not result:
        await compiler.finish("出错了，请稍后再试")
    else:
        await compiler.finish(
            result["output"] if result["output"] else result["errors"]
        )
