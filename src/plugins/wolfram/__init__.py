import re
import subprocess
from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp import Bot, Event, unescape

from .data_source import get_wolframalpha_simple, get_wolframalpha_text

export = export()
export.description = 'WolframAlpha计算知识引擎'
export.usage = 'Usage:\n  wolfram {text}'
export.options = 'Options:\n  -p, --plaintext 纯文本结果'
export.help = export.description + '\n' + export.usage + '\n' + export.options

wolfram_parser = ArgumentParser()
wolfram_parser.add_argument('-p', '--plaintext', type=int, default=2)
wolfram_parser.add_argument('equation', nargs='+')

wolfram = on_command('wolfram', aliases={'wolframalpha'}, priority=34)


@wolfram.handle()
async def _(bot: Bot, event: Event, state: T_State):
    text = unescape(event.get_plaintext()).strip()

    plaintext = False
    pattern = [r'-p +.*?', r'.*? +-p', r'--plaintext +.*?', r'.*? +--plaintext']
    for p in pattern:
        if re.fullmatch(p, text):
            plaintext = True
            break
    text = text.replace('-p', '').replace('--plaintext', '').strip()
    if not text:
        await wolfram.finish(export.usage)

    if not re.fullmatch(r'[\x00-\x7F]+', text):
        text = subprocess.getoutput(f'trans -t en -brief -no-warn "{text}"').strip()
        if text:
            await wolfram.send('使用如下翻译进行搜索：\n' + text)
        else:
            await wolfram.finish('出错了，请稍后再试')

    if plaintext:
        msg = await get_wolframalpha_text(text)
    else:
        msg = await get_wolframalpha_simple(text)
    if not msg:
        await wolfram.finish('出错了，请稍后再试')

    await wolfram.finish(msg)
