from nonebot import on_shell_command
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent

from .monitor import *
from .dynmap import get_status, send_message
from .dynmap_list import get_dynmap_url, bind_dynmap, unbind_dynmap, open_dynmap_chat, close_dynmap_chat, get_dynmap_list, set_user

dynmap_parser = ArgumentParser()
dynmap_parser.add_argument('arg', nargs='+')
dynmap = on_shell_command('dynmap', parser=dynmap_parser, priority=38)


@dynmap.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    if not hasattr(args, 'arg'):
        await dynmap.finish()
    state['arg'] = args.arg


@dynmap.got('arg')
async def _(bot: Bot, event: Event, state: T_State):
    args = state['arg']
    state['command'] = args[0]
    if len(args) >= 2:
        state['arg1'] = args[1]
    if len(args) == 3:
        state['arg2'] = args[2]
    if len(args) > 3:
        await dynmap.finish()


def get_id(event: Event):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.get_user_id())


@dynmap.got('command')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    if command not in ['bind', 'unbind', 'chat', 'status', 'login', 'send']:
        await dynmap.finish()

    user_id = get_id(event)
    state['user_id'] = user_id

    if command in ['unbind', 'chat', 'status', 'login', 'send']:
        dynmap_url = await get_dynmap_url(user_id)
        if not dynmap_url:
            await dynmap.finish('目前还没有绑定动态地图，使用“dynmap bind <url>”绑定')

    if command in ['bind']:
        if 'arg1' not in state.keys():
            await dynmap.finish('Usage: dynmap bind <url>')
        url = state['arg1']
        url_ok = await bind_dynmap(user_id, url)
        if not url_ok:
            await dynmap.finish('出错了，请检查链接或稍后再试')
        await dynmap.finish('成功绑定动态地图，使用“dynmap chat on/off”开启或关闭聊天转发；使用“dynmap status”查看在线状态')
    elif command in ['unbind']:
        await unbind_dynmap(user_id)
        await dynmap.finish('成功解绑动态地图')
    elif command in ['chat']:
        if 'arg1' not in state.keys():
            await dynmap.finish('Usage: dynmap chat on/off')
        action = state['arg1']
        if action not in ['on', 'off']:
            await dynmap.finish('Usage: dynmap chat on/off')
        if action in ['on']:
            await open_dynmap_chat(user_id)
            await dynmap.finish('聊天转发已打开')
        elif action in ['off']:
            await close_dynmap_chat(user_id)
            await dynmap.finish('聊天转发已关闭')
    elif command in ['status']:
        url = get_dynmap_list()[user_id]['update_url']
        status = await get_status(url)
        if not status:
            await dynmap.finish('出错了，请稍后再试')
        await dynmap.finish(status)
    elif command in ['login']:
        if ('arg1' not in state.keys()) or ('arg2' not in state.keys()):
            await dynmap.finish('Usage: dynmap login <username> <password>')
        await set_user(user_id, state['arg1'], state['arg2'])
        await dynmap.finish('登录成功')
    elif command in ['send']:
        if 'arg1' not in state.keys():
            await dynmap.finish('Usage: dynmap send <message>')
        config = get_dynmap_list()[user_id]
        if not ('username' in config and 'password' in config):
            await dynmap.finish('尚未登录，使用“dynmap login <username> <password>”登录')
        if not await send_message(config, state['arg1']):
            await dynmap.finish('发送消息失败')
