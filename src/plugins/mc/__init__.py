from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent

from .dynmap_list import get_dynmap_url, bind_dynmap, unbind_dynmap, open_dynmap_chat, close_dynmap_chat, get_dynmap_status


dynmap = on_command('dynmap', priority=38)


@dynmap.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = str(event.get_plaintext()).strip().split()
    args = [s.strip() for s in args]
    args = [s for s in args if s]
    if not args:
        await dynmap.finish()
    state['args'] = args


@dynmap.got('args')
async def _(bot: Bot, event: Event, state: T_State):
    args = state['args']
    state['command'] = args[0]
    if len(args) == 2:
        state['arg'] = args[1]
    if len(args) > 2:
        await dynmap.finish()


def get_id(event: Event):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.get_user_id())


@dynmap.got('command')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    if command not in ['bind', 'unbind', 'chat', 'status']:
        await dynmap.finish()

    user_id = get_id(event)
    state['user_id'] = user_id

    if command in ['unbind', 'chat', 'status']:
        dynmap_url = await get_dynmap_url(user_id)
        if not dynmap_url:
            await dynmap.finish('目前还没有绑定动态地图，使用“dynmap bind <url>”绑定')

    if command in ['bind']:
        if 'arg' not in state.keys():
            await dynmap.finish('Usage: dynmap bind <url>')
        url = state['arg']
        url_ok = await bind_dynmap(user_id, url)
        if not url_ok:
            await dynmap.finish('出错了，请检查链接或稍后再试')
        await dynmap.finish('成功绑定动态地图，使用“dynmap chat on/off”展示或关闭聊天消息；使用“dynmap status”查看在线状态')
    elif command in ['unbind']:
        await unbind_dynmap(user_id)
        await dynmap.finish('成功解绑动态地图')
    elif command in ['chat']:
        if 'arg' not in state.keys():
            await dynmap.finish('Usage: dynmap chat on/off')
        action = state['arg']
        if action not in ['on', 'off']:
            await dynmap.finish('Usage: dynmap chat on/off')
        if action in ['on']:
            await open_dynmap_chat(user_id)
            await dynmap.finish('动态地图聊天显示已打开')
        elif action in ['off']:
            await close_dynmap_chat(user_id)
            await dynmap.finish('动态地图聊天显示已关闭')
    elif command in ['status']:
        url = await get_dynmap_url(user_id)
        status = await get_dynmap_status(url)
        if not status:
            await dynmap.finish('出错了，请稍后再试')
        await dynmap.finish()
