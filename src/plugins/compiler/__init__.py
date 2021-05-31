import re
from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, unescape
from nonebot.log import logger

from .data_source import legal_language, network_compile

export = export()
export.description = '网络编译器'
export.usage = 'Usage:\n  lang {language};\n  {code}'
export.options = 'Options:\n  ' + f"支持的语言：{', '.join(list(legal_language.keys()))}"
export.notice = 'Notice:\n  来源为菜鸟教程的网络编译器'
export.help = export.description + '\n' + export.usage + '\n' + export.options + '\n' + export.notice

compiler = on_command('lang', priority=20)


@compiler.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = unescape(event.get_plaintext()).strip()

    match_obj = re.match(r'(.*?)[;\n]+(.*)', msg, re.S)
    if not match_obj:
        await compiler.finish(export.usage + '\n' + export.options)

    language = match_obj.group(1)
    if language not in legal_language:
        await compiler.finish(export.options)

    code = match_obj.group(2)
    if not code:
        return
    result = await network_compile(language, code)
    logger.debug(result)
    if isinstance(result, str):
        await compiler.send(message=result)
        await compiler.finish()
    else:
        await compiler.send(message=result["output"] if result["output"] else result["errors"])
        await compiler.finish()
