from nonebot import on_command, on_shell_command, on_notice
from nonebot.typing import T_State
from nonebot.rule import ArgumentParser
from nonebot.adapters.cqhttp.bot import Bot
from nonebot.adapters.cqhttp.event import Event, GroupMessageEvent, PokeNotifyEvent

from .data_source import get_mcstatus, get_mc_uuid, get_crafatar, get_mcmodel
from .monitor import *
from .dynmap_source import get_status, send_message
from .dynmap_list import get_dynmap_url, bind_dynmap, unbind_dynmap, \
    open_dynmap_chat, close_dynmap_chat, open_poke_status, close_poke_status, get_dynmap_list, set_user


__des__ = 'Minecraft相关功能'
__cmd__ = '''
1、mcstatus {url}，MC服务器状态查询
2、mc avatar/head/body/skin/cape/model {id}，获取MC用户的 头像/头/身体/皮肤/披风/全身动图
3、dynmap bind {url}，动态地图相关功能
'''.strip()
__short_cmd__ = 'mcstatus、mcskin 等'
__example__ = '''
mcstatus mczju.tpddns.cn
mcskin hsds
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


mc = on_command('mc', priority=38)


@mc.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.get_plaintext().strip()
    if not msg:
        await mc.finish()
    if msg.startswith('status'):
        addr = msg.replace('status', '', 1).strip()
        if addr:
            status = await get_mcstatus(addr)
            if status:
                await mc.finish(status)
            else:
                await mc.finish('出错了，请稍后再试')
    else:
        types = ['avatar', 'head', 'body', 'skin', 'cape', 'model']
        for t in types:
            if msg.startswith(t):
                username = msg.replace(t, '', 1).strip()
                if username:
                    uuid = await get_mc_uuid(username)
                    if not uuid:
                        await mc.finish('出错了，请稍后再试')
                    if uuid == 'none':
                        await mc.finish('找不到该用户')
                    if t == 'model':
                        await mc.send('生成中，请耐心等待。。。')
                        result = await get_mcmodel(uuid)
                    else:
                        result = await get_crafatar(t, uuid)
                    if result:
                        await mc.finish(result)
                    else:
                        await mc.finish('出错了，请稍后再试')
    await mc.finish()


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
    if isinstance(event, GroupMessageEvent) or isinstance(event, PokeNotifyEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.get_user_id())


@dynmap.got('command')
async def _(bot: Bot, event: Event, state: T_State):
    command = state['command']
    if command not in ['bind', 'unbind', 'chat', 'poke', 'status', 'login', 'send']:
        await dynmap.finish()

    user_id = get_id(event)
    state['user_id'] = user_id

    if command in ['unbind', 'chat', 'poke', 'status', 'login', 'send']:
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
    elif command in ['poke']:
        if 'arg1' not in state.keys():
            await dynmap.finish('Usage: dynmap poke on/off')
        action = state['arg1']
        if action not in ['on', 'off']:
            await dynmap.finish('Usage: dynmap poke on/off')
        if action in ['on']:
            await open_poke_status(user_id)
            await dynmap.finish('已打开戳一戳状态显示')
        elif action in ['off']:
            await close_poke_status(user_id)
            await dynmap.finish('已关闭戳一戳状态显示')
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


async def _poke_status(bot: Bot, event: Event, state: T_State) -> bool:
    if isinstance(event, PokeNotifyEvent) and event.is_tome():
        user_id = get_id(event)
        dynmap_list = get_dynmap_list()
        if user_id in dynmap_list:
            if dynmap_list[user_id]['poke']:
                return True
    return False


poke_status = on_notice(_poke_status, priority=38, block=True)


@poke_status.handle()
async def _(bot: Bot, event: Event, state: T_State):
    user_id = get_id(event)
    url = get_dynmap_list()[user_id]['update_url']
    status = await get_status(url)
    if not status:
        await poke_status.finish('出错了，请稍后再试')
    await poke_status.finish(status)
