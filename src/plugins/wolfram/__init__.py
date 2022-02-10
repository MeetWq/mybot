import re
import subprocess
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from .data_source import get_wolframalpha_simple, get_wolframalpha_text


__des__ = "WolframAlpha计算引擎"
__cmd__ = """
wolfram {text}
""".strip()
__short_cmd__ = __cmd__
__example__ = """
wolfram int x
""".strip()
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"


wolfram = on_command("wolfram", aliases={"wolframalpha"}, block=True, priority=12)


@wolfram.handle()
async def _(msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()

    plaintext = False
    pattern = [r"-p +.*?", r".*? +-p", r"--plaintext +.*?", r".*? +--plaintext"]
    for p in pattern:
        if re.fullmatch(p, text):
            plaintext = True
            break
    text = text.replace("-p", "").replace("--plaintext", "").strip()
    if not text:
        await wolfram.finish()

    if not re.fullmatch(r"[\x00-\x7F]+", text):
        text = subprocess.getoutput(f'trans -t en -brief -no-warn "{text}"').strip()
        if text:
            await wolfram.send("使用如下翻译进行搜索：\n" + text)
        else:
            await wolfram.finish("出错了，请稍后再试")

    if plaintext:
        res = await get_wolframalpha_text(text)
    else:
        res = await get_wolframalpha_simple(text)
    if not res:
        await wolfram.finish("出错了，请稍后再试")

    await wolfram.finish(res)
