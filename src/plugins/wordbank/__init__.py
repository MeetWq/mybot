import re
import random
from nonebot.matcher import Matcher
from nonebot import on_command, on_message
from nonebot.params import CommandArg, EventMessage, Depends
from nonebot.adapters.onebot.v11 import Message, MessageEvent, GroupMessageEvent, unescape
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER, GROUP_ADMIN, PRIVATE_FRIEND

from .data_source import WordBank
from .util import parse


__des__ = '词库'
__cmd__ = '''
添加词条 [@/正则/模糊]问xxx答xxx，默认为全匹配，“正则问”为正则匹配，“模糊”问为关键词匹配，加“@”为@我才会触发
删除词条 xxx
清空词库

回答中可使用“/user”代表发送人昵称，“/atuser”代表@发送人
'''.strip()
__short_cmd__ = '添加词条 问xxx答xxx'
__example__ = '''
添加词条 问 你好 答 嗯，我好
添加词条 模糊问 你好 答 /user，你好
添加词条 @模糊问 你好 答 /atuser 你好呀
删除词条 你好
'''.strip()
__notice__ = '仅群管理员或超级用户可增删词条'
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}\nNotice:\n{__notice__}'


PEM_RW = SUPERUSER | GROUP_OWNER | GROUP_ADMIN | PRIVATE_FRIEND
PEM_GL = SUPERUSER


def get_id(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.user_id)


wb = WordBank()

wordbank = on_message(priority=39)


@wordbank.handle()
async def _(event: MessageEvent, msg: Message = EventMessage()):
    msg = unescape(str(msg)).strip()
    user_id = get_id(event)
    results = wb.match(user_id, msg, event.is_tome())
    if results:
        wordbank.block = True
        res = random.choice(results)
        nickname = event.sender.card or event.sender.nickname
        sender_id = event.sender.user_id
        res = parse(res, nickname, sender_id)
        await wordbank.finish(Message(unescape(res)))
    else:
        wordbank.block = False
        await wordbank.finish()


add_cmd = on_command('添加词条', block=True, priority=14, permission=PEM_RW)
add_cmd_gl = on_command('添加全局词条', block=True, priority=14, permission=PEM_GL)


@add_cmd.handle()
async def _(msg: Message = CommandArg(), user_id: str = Depends(get_id)):
    await wb_add(add_cmd, msg, user_id)


@add_cmd_gl.handle()
async def _(msg: Message = CommandArg()):
    await wb_add(add_cmd_gl, msg, user_id='0')


async def wb_add(matcher: Matcher, msg: Message, user_id: str):
    msg = unescape(str(msg))
    pattern = r"\s*(@|模糊|正则)*\s*问(.+?)答(.+)"
    match = re.match(pattern, msg, re.S)
    if match:
        type, key, value = match.groups()
        key = key.strip()
        value = value.lstrip()
        flag = 0 if not type else 2 if '模糊' in type else 1 if '正则' in type else 0
        key = '@' + key if (type and '@' in type) else key
        res = wb.add(user_id, key, value, flag)
        if res:
            await matcher.finish('我记住了~')


rm_cmd = on_command('删除词条', block=True, priority=14, permission=PEM_RW)
rm_cmd_gl = on_command('删除全局词条', block=True, priority=14, permission=PEM_GL)


@rm_cmd.handle()
async def _(msg: Message = CommandArg(), user_id: str = Depends(get_id)):
    await wb_rm(rm_cmd, msg, user_id)


@rm_cmd_gl.handle()
async def _(msg: Message = CommandArg()):
    await wb_rm(rm_cmd_gl, msg, user_id='0')


async def wb_rm(matcher: Matcher, msg: Message, user_id: str):
    msg = unescape(str(msg)).strip()
    res = wb.remove(user_id, msg)
    if res:
        await matcher.send('删除成功~')


clear_cmd = on_command('清空词库', block=True, priority=14, permission=PEM_RW)
clear_cmd_gl = on_command('清空全局词库', block=True, priority=14, permission=PEM_GL)


@clear_cmd.handle()
async def _(user_id: str = Depends(get_id)):
    await wb_rm(clear_cmd, user_id)


@clear_cmd_gl.handle()
async def _():
    await wb_rm(clear_cmd_gl, user_id='0')


async def wb_clear(matcher: Matcher, user_id: str):
    res = wb.clear(user_id)
    if res:
        await matcher.send('清空成功~')
