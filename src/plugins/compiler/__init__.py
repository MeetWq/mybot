from nonebot import on_regex
from nonebot.params import RegexDict

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


compiler = on_regex(r'^lang\s+(?P<language>[^;；\s]+)[;；\s]+(?P<code>[^;；\s]+.*)',
                    block=True, priority=13)


@compiler.handle()
async def _(msg: dict = RegexDict()):
    language = str(msg['language']).strip()
    code = str(msg['code']).strip()
    if language not in legal_language:
        await compiler.finish(f"支持的语言：{', '.join(list(legal_language.keys()))}")

    result = await network_compile(language, code)
    if not result:
        await compiler.finish('出错了，请稍后再试')
    else:
        await compiler.finish(result['output'] if result['output'] else result['errors'])
