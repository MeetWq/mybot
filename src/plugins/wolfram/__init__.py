import langid
import subprocess
from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import get_wolframalpha_simple

export = export()
export.description = 'WolframAlpha计算知识引擎'
export.usage = 'Usage:\n  wolfram {text}'
export.help = export.description + '\n' + export.usage

wolfram = on_command('wolfram', aliases={'wolframalpha'}, priority=34)


@wolfram.handle()
async def _(bot: Bot, event: Event, state: T_State):
    text = str(event.get_message()).strip()
    if not text:
        await wolfram.finish(export.usage)

    if langid.classify(text)[0] not in ['en', 'es']:
        text = subprocess.getoutput(f'trans -t en -brief -no-warn "{text}"').strip()
        if text:
            await wolfram.send('WolframAlpha 仅支持英文，将使用如下翻译进行搜索：\n' + text)
        else:
            await wolfram.finish('出错了，请稍后再试')

    msg = await get_wolframalpha_simple(text)
    if not msg:
        await wolfram.finish('出错了，请稍后再试')

    await wolfram.send(message=msg)
    await wolfram.finish()
