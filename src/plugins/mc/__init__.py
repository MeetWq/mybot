from argparse import Namespace
from nonebot.matcher import Matcher
from nonebot.rule import Rule, ArgumentParser
from nonebot import on_command, on_shell_command, on_notice
from nonebot.params import CommandArg, ShellCommandArgs, Depends
from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent, PokeNotifyEvent, Message, MessageSegment

from .monitor import *
from .dynmap_list import *
from .dynmap_source import get_status, send_message
from .data_source import get_mcstatus, get_mc_uuid, get_crafatar, get_mcmodel


__des__ = 'Minecraft相关功能'
__cmd__ = '''
1、mcstatus {url}，MC服务器状态查询
2、mc avatar/head/body/skin/cape/model {id}，获取MC用户的 头像/头/身体/皮肤/披风/全身动图
3、dynmap bind {url}，动态地图相关功能
'''.strip()
__example__ = '''
mcstatus mczju.tpddns.cn
mcskin hsds
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


mc = on_command('mc', block=True, priority=12)


@mc.handle()
async def _(arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
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
                        await mc.finish(MessageSegment.image(result))
                    else:
                        await mc.finish('出错了，请稍后再试')
    await mc.finish()


async def bind(matcher: Matcher, user_id: str, url: str, **kwargs):
    result = await bind_dynmap(user_id, url)
    if not result:
        await matcher.finish('出错了，请检查链接或稍后再试')
    await matcher.finish('成功绑定动态地图，使用“dynmap chaton/chatoff”开启或关闭聊天转发；使用“dynmap status”查看在线状态')


async def unbind(matcher: Matcher, user_id: str, **kwargs):
    if not unbind_dynmap(user_id):
        await matcher.finish('尚未绑定动态地图')
    await matcher.finish('成功解绑动态地图')


async def chaton(matcher: Matcher, user_id: str, **kwargs):
    if not open_chat(user_id):
        await matcher.finish('尚未绑定动态地图')
    await matcher.finish('聊天转发已打开')


async def chatoff(matcher: Matcher, user_id: str, **kwargs):
    if not close_chat(user_id):
        await matcher.finish('尚未绑定动态地图')
    await matcher.finish('聊天转发已关闭')


async def pokeon(matcher: Matcher, user_id: str, **kwargs):
    if not open_poke(user_id):
        await matcher.finish('尚未绑定动态地图')
    await matcher.finish('已打开戳一戳状态显示')


async def pokeoff(matcher: Matcher, user_id: str, **kwargs):
    if not close_poke(user_id):
        await matcher.finish('尚未绑定动态地图')
    await matcher.finish('已关闭戳一戳状态显示')


async def status(matcher: Matcher, user_id: str, **kwargs):
    url = get_update_url(user_id)
    if not url:
        await matcher.finish('尚未绑定动态地图')
    status = await get_status(url)
    if not status:
        await matcher.finish('出错了，请稍后再试')
    await matcher.finish(status)


async def login(matcher: Matcher, user_id: str, username: str, password: str, **kwargs):
    set_user(user_id, username, password)
    await matcher.finish('登录成功')


async def logout(matcher: Matcher, user_id: str, **kwargs):
    del_user(user_id)
    await matcher.finish('注销成功')


async def send(matcher: Matcher, user_id: str, message: str, **kwargs):
    if not get_login_status(user_id):
        await matcher.finish('尚未登录，使用“dynmap login <username> <password>”登录')
    if not await send_message(get_dynmap_list()[user_id], message):
        await matcher.finish('发送消息失败')


dynmap_parser = ArgumentParser('dynmap')

dynmap_subparsers = dynmap_parser.add_subparsers()

bind_parser = dynmap_subparsers.add_parser('bind', aliases=('绑定'))
bind_parser.add_argument('url')
bind_parser.set_defaults(func=bind)

unbind_parser = dynmap_subparsers.add_parser('unbind', aliases=('解绑'))
unbind_parser.set_defaults(func=unbind)

login_parser = dynmap_subparsers.add_parser('login', aliases=('登录'))
login_parser.add_argument('username')
login_parser.add_argument('password')
login_parser.set_defaults(func=login)

logout_parser = dynmap_subparsers.add_parser('logout', aliases=('退出'))
logout_parser.set_defaults(func=logout)

send_parser = dynmap_subparsers.add_parser('send', aliases=('发送'))
send_parser.add_argument('message')
send_parser.set_defaults(func=send)

status_parser = dynmap_subparsers.add_parser('status', aliases=('状态'))
status_parser.set_defaults(func=status)

pokeon_parser = dynmap_subparsers.add_parser('pokeon')
pokeon_parser.set_defaults(func=pokeon)

pokeoff_parser = dynmap_subparsers.add_parser('pokeoff')
pokeoff_parser.set_defaults(func=pokeoff)

chaton_parser = dynmap_subparsers.add_parser('chaton')
chaton_parser.set_defaults(func=chaton)

chatoff_parser = dynmap_subparsers.add_parser('chatoff')
chatoff_parser.set_defaults(func=chatoff)

dynmap = on_shell_command('dynmap', parser=dynmap_parser,
                          block=True, priority=15)


def get_id(event: Event):
    if isinstance(event, GroupMessageEvent) or isinstance(event, PokeNotifyEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.get_user_id())


@dynmap.handle()
async def _(args: Namespace = ShellCommandArgs(), user_id: str = Depends(get_id)):
    args.matcher = dynmap
    args.user_id = user_id

    if hasattr(args, 'func'):
        await args.func(**args)


async def _poke_status(event: Event) -> bool:
    if isinstance(event, PokeNotifyEvent) and event.is_tome():
        user_id = get_id(event)
        dynmap_list = get_dynmap_list()
        if user_id in dynmap_list:
            if dynmap_list[user_id]['poke']:
                return True
    return False


poke_status = on_notice(Rule(_poke_status), priority=15, block=False)


@poke_status.handle()
async def _(event: Event, user_id: str = Depends(get_id)):
    await status(poke_status, user_id)
