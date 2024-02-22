import traceback
from argparse import Namespace
from typing import Union

from nonebot import on_shell_command, require
from nonebot.adapters import Event
from nonebot.exception import ParserExit
from nonebot.log import logger
from nonebot.params import ShellCommandArgs
from nonebot.plugin import PluginMetadata
from nonebot.rule import ArgumentParser

require("nonebot_plugin_orm")
require("nonebot_plugin_saa")
require("nonebot_plugin_htmlrender")
require("nonebot_plugin_apscheduler")

from nonebot_plugin_saa import PlatformTarget, enable_auto_select_bot, extract_target

enable_auto_select_bot()

from . import migrations
from .blrec import server
from .blrec.task import sync_tasks
from .config import Config
from .database.db import (
    add_sub,
    del_sub,
    get_sub,
    get_subs,
    get_user,
    get_users,
    update_sub_options,
)
from .models import BiliUser, Subscription, SubscriptionOptions
from .pusher import dynamic_pusher, live_pusher
from .utils import get_user_info_by_name, get_user_info_by_uid

usage = (
    "添加订阅：blive d 用户名/UID\n"
    "取消订阅：blive td 用户名/UID\n"
    "订阅列表：blive list\n"
    "开启直播：blive liveon 用户名/UID\n"
    "关闭直播：blive liveoff 用户名/UID\n"
    "开启动态：blive dynon 用户名/UID\n"
    "关闭动态：blive dynoff 用户名/UID\n"
    "开启录播：blive recon 用户名/UID\n"
    "关闭录播：blive recoff 用户名/UID"
)

__plugin_meta__ = PluginMetadata(
    name="B站用户订阅",
    description="B站用户直播、动态订阅，自动录播",
    usage=usage,
    config=Config,
    extra={
        "example": "blive d 小南莓Official\nblive recon 小南莓Official",
        "notice": "注意是UID不是房间号",
        "orm_version_location": migrations,
    },
)


async def add_sub_func(target: PlatformTarget, user: BiliUser):
    if await get_sub(target, user.uid):
        await blive.finish(f"{user.name} 已经订阅过了")

    await add_sub(Subscription(target=target, user=user, options=SubscriptionOptions()))

    await blive.finish(f"成功添加订阅 {user.name}")


async def del_sub_func(target: PlatformTarget, user: BiliUser):
    if not await get_sub(target, user.uid):
        await blive.finish(f"{user.name} 还没有订阅过")

    await del_sub(target, user.uid)

    await blive.finish(f"成功取消订阅 {user.name}")


async def list_sub_func(target: PlatformTarget, _):
    subs = await get_subs(target)
    if not subs:
        await blive.finish("目前还没有任何订阅")

    msg = "已订阅以下用户:\n"
    for sub in subs:
        user = sub.user
        options = sub.options
        msg += (
            f"\n{user.name} "
            f"{'(直播)' if user.room_id and options.live else ''}"
            f"{'(动态)' if options.dynamic else ''}"
            f"{'(录播)' if user.room_id and options.record else ''}"
        )
    await blive.finish(msg)


async def liveon_func(target: PlatformTarget, user: BiliUser):
    if not (sub := await get_sub(target, user.uid)):
        await blive.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.live = True
    await update_sub_options(target, user.uid, options)

    await blive.finish(f"{user.name} 直播推送已打开")


async def liveoff_func(target: PlatformTarget, user: BiliUser):
    if not (sub := await get_sub(target, user.uid)):
        await blive.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.live = False
    await update_sub_options(target, user.uid, options)

    await blive.finish(f"{user.name} 直播推送已关闭")


async def dynon_func(target: PlatformTarget, user: BiliUser):
    if not (sub := await get_sub(target, user.uid)):
        await blive.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.dynamic = True
    await update_sub_options(target, user.uid, options)

    await blive.finish(f"{user.name} 动态推送已打开")


async def dynoff_func(target: PlatformTarget, user: BiliUser):
    if not (sub := await get_sub(target, user.uid)):
        await blive.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.dynamic = False
    await update_sub_options(target, user.uid, options)

    await blive.finish(f"{user.name} 动态推送已关闭")


async def recon_func(target: PlatformTarget, user: BiliUser):
    if not (sub := await get_sub(target, user.uid)):
        await blive.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.record = True
    await update_sub_options(target, user.uid, options)

    await blive.send(f"{user.name} 自动录播已打开")
    await sync_tasks()


async def recoff_func(target: PlatformTarget, user: BiliUser):
    if not (sub := await get_sub(target, user.uid)):
        await blive.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.record = False
    await update_sub_options(target, user.uid, options)

    await blive.send(f"{user.name} 自动录播已关闭")
    await sync_tasks()


blive_parser = ArgumentParser("blive")

blive_subparsers = blive_parser.add_subparsers()

add_parser = blive_subparsers.add_parser("add", aliases=("d", "添加", "添加订阅"))
add_parser.add_argument("name")
add_parser.set_defaults(func=add_sub_func)

del_parser = blive_subparsers.add_parser("del", aliases=("td", "删除", "取消订阅"))
del_parser.add_argument("name")
del_parser.set_defaults(func=del_sub_func)

list_parser = blive_subparsers.add_parser("list", aliases=("列表", "订阅列表"))
list_parser.set_defaults(func=list_sub_func)

liveon_parser = blive_subparsers.add_parser("liveon", aliases=("开启直播"))
liveon_parser.add_argument("name")
liveon_parser.set_defaults(func=liveon_func)

liveoff_parser = blive_subparsers.add_parser("liveoff", aliases=("关闭直播"))
liveoff_parser.add_argument("name")
liveoff_parser.set_defaults(func=liveoff_func)

dynon_parser = blive_subparsers.add_parser("dynon", aliases=("开启动态"))
dynon_parser.add_argument("name")
dynon_parser.set_defaults(func=dynon_func)

dynoff_parser = blive_subparsers.add_parser("dynoff", aliases=("关闭动态"))
dynoff_parser.add_argument("name")
dynoff_parser.set_defaults(func=dynoff_func)

recon_parser = blive_subparsers.add_parser("recon", aliases=("开启录播"))
recon_parser.add_argument("name")
recon_parser.set_defaults(func=recon_func)

recoff_parser = blive_subparsers.add_parser("recoff", aliases=("关闭录播"))
recoff_parser.add_argument("name")
recoff_parser.set_defaults(func=recoff_func)


blive = on_shell_command(
    "blive",
    aliases={"bilibili_live", "B站直播间", "b站直播间"},
    block=True,
    parser=blive_parser,
    priority=12,
)


@blive.handle()
async def _(event: Event, ns: Union[Namespace, ParserExit] = ShellCommandArgs()):
    if isinstance(ns, ParserExit):
        if ns.status == 0:
            await blive.finish(f"B站用户直播、动态订阅\nusage:\n{usage}")
        return

    try:
        target = extract_target(event)
    except RuntimeError:
        return

    user = None
    if hasattr(ns, "name"):
        name = str(ns.name)
        if name.isdigit():
            uid = name
            user = await get_user(uid)
            if not user:
                try:
                    user = await get_user_info_by_uid(uid)
                except:
                    logger.warning(traceback.format_exc())
        else:
            users = await get_users()
            for sub_user in users:
                if sub_user.name == name:
                    user = sub_user
            if not user:
                try:
                    user = await get_user_info_by_name(name)
                except:
                    logger.warning(traceback.format_exc())

        if not user:
            await blive.finish("获取用户信息失败，请检查名称或稍后再试")

    if hasattr(ns, "func"):
        await ns.func(target, user)
