import shlex
from typing import Type
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message

from .data_source import commands, get_essay

__plugin_meta__ = PluginMetadata(
    name="短文生成器",
    description="CP文、毒鸡汤等多种短文生成",
    usage="\n".join(
        [f"{i}. {c['help']}" for i, c in enumerate(commands.values(), start=1)]
    ),
    extra={
        "example": "CP文 攻 受\n",
    },
)


async def handle(matcher: Type[Matcher], type: str, text: str):
    arg_num = commands[type].get("arg_num", 1)
    texts = shlex.split(text) if arg_num > 1 else [text]
    if not arg_num:
        texts = []
    elif arg_num != len(texts):
        await matcher.finish(f"Usage:\n{commands[type]['help']}")
    res = await get_essay(type, texts)
    if res:
        await matcher.finish(res)
    else:
        await matcher.finish("出错了，请稍后再试")


def create_matchers():
    def create_handler(type: str) -> T_Handler:
        async def handler(msg: Message = CommandArg()):
            text = msg.extract_plain_text().strip()
            await handle(matcher, type, text)

        return handler

    for type, params in commands.items():
        matcher = on_command(type, aliases=params["aliases"], block=True, priority=13)
        matcher.append_handler(create_handler(type))


create_matchers()
