import re
import random
from nonebot import on_command, on_message
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, MessageEvent, GroupMessageEvent, unescape
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import GROUP_OWNER, GROUP_ADMIN, PRIVATE_FRIEND

from .data_source import WordBank
from .util import parse


def get_id(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.user_id)


wb = WordBank()

wordbank = on_message(priority=39)


@wordbank.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    user_id = get_id(event)
    msgs = wb.match(user_id, unescape(event.raw_message))
    if msgs:
        msg = random.choice(msgs)
        await wordbank.finish(Message(unescape(parse(msg, event))))


add_cmd = on_command('添加词条', priority=14,
                     permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN | PRIVATE_FRIEND)
add_cmd_gl = on_command('添加全局词条', priority=14, permission=SUPERUSER)


@add_cmd.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await wb_add(add_cmd, event)


@add_cmd_gl.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await wb_add(add_cmd_gl, event, gl=True)


async def wb_add(matcher: Matcher, event: MessageEvent, gl: bool = False):
    user_id = '0' if gl else get_id(event)
    msg = unescape(event.raw_message)
    pattern = r"\s*(?:模糊|正则)*\s*问(.+?)答(.+)"
    match = re.match(pattern, msg, re.S)
    if match:
        type, key, value = match.groups()
        flag = 2 if '模糊' in type else 1 if '正则' in type else 0
        res = wb.add(user_id, key, value, flag)
        if res:
            await add_cmd.finish('我记住了~')


rm_cmd = on_command('删除词条', priority=14,
                    permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN | PRIVATE_FRIEND)
rm_cmd_gl = on_command('删除全局词条', priority=14, permission=SUPERUSER)


@rm_cmd.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await wb_rm(rm_cmd, event)


@rm_cmd_gl.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await wb_rm(rm_cmd_gl, event, gl=True)


async def wb_rm(matcher: Matcher, event: MessageEvent, gl: bool = False):
    user_id = '0' if gl else get_id(event)
    msg = unescape(event.message)
    res = wb.remove(user_id, msg)
    if res:
        await rm_cmd.send('删除成功~')


clear_cmd = on_command('清空词库', priority=14,
                       permission=SUPERUSER | GROUP_OWNER | PRIVATE_FRIEND)
clear_cmd_gl = on_command('清空全局词库', priority=14, permission=SUPERUSER)


@clear_cmd.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await wb_rm(clear_cmd, event)


@clear_cmd_gl.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    await wb_rm(clear_cmd_gl, event, gl=True)


async def wb_clear(matcher: Matcher, event: MessageEvent, gl: bool = False):
    user_id = '0' if gl else get_id(event)
    res = wb.clear(user_id)
    if res:
        await rm_cmd.send('清空成功~')
