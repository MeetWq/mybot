import re
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, unescape

from .data_source import legal_language, network_compile


__des__ = '网络编译器'
__cmd__ = f'''
lang {{language}};
{{code}}

支持的语言：{', '.join(list(legal_language.keys()))}
'''.strip()
__short_cmd__ = 'lang {language}; {code}'
__example__ = '''
lang py3;
print('hello')
'''.strip()
__notice__ = '来源为菜鸟教程的网络编译器，不要试图搞事情'
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}\nNotice:\n{__notice__}'


compiler = on_command('lang', priority=20)


@compiler.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = unescape(event.get_plaintext()).strip()

    match_obj = re.match(r'(.*?)[;；\s]+(.*)', msg, re.S)
    if not match_obj:
        await compiler.finish()

    code = match_obj.group(2)
    if not code:
        return

    language = match_obj.group(1)
    if language not in legal_language:
        await compiler.finish(f"支持的语言：{', '.join(list(legal_language.keys()))}")

    result = await network_compile(language, code)
    if not result:
        await compiler.finish('出错了，请稍后再试')
    else:
        await compiler.finish(result['output'] if result['output'] else result['errors'])
