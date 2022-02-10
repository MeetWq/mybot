from typing import Type
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from .data_source import get_text, commands


__des__ = "抽象话等多种文本生成"
cmd = "/".join([list(c["aliases"])[0] for c in commands.values()])
__cmd__ = f"""
{cmd} {{text}}
""".strip()
__short_cmd__ = "抽象话、火星文 等"
__example__ = """
抽象话 那真的牛逼
火星文 那真的牛逼
""".strip()
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"


async def handle(matcher: Type[Matcher], type: str, text: str):
    res = await get_text(type, text)
    if res:
        await matcher.finish(res)
    else:
        await matcher.finish("出错了，请稍后再试")


def create_matchers():
    def create_handler(type: str) -> T_Handler:
        async def handler(msg: Message = CommandArg()):
            text = msg.extract_plain_text().strip()
            if text:
                await handle(matcher, type, text)

        return handler

    for type, params in commands.items():
        matcher = on_command(
            f"{type}text", aliases=params["aliases"], block=True, priority=13
        )
        matcher.append_handler(create_handler(type))


create_matchers()
