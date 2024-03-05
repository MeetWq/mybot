import traceback

from nonebot import require
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_orm")
require("nonebot_plugin_saa")
require("nonebot_plugin_alconna")
require("nonebot_plugin_htmlrender")
require("nonebot_plugin_localstore")
require("nonebot_plugin_apscheduler")

from arclet.alconna import Field
from nonebot_plugin_alconna import Alconna, Args, Subcommand, on_alconna
from nonebot_plugin_saa import SaaTarget, enable_auto_select_bot

enable_auto_select_bot()

from . import login as login
from . import migrations
from .blrec import server as server
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
from .pusher import dynamic_pusher as dynamic_pusher
from .pusher import live_pusher as live_pusher
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


arg_name = Args["name", str, Field(completion=lambda: "B站用户名/UID")]

blive = on_alconna(
    Alconna(
        "blive",
        Subcommand("add", arg_name, alias={"d", "添加", "添加订阅"}),
        Subcommand("del", arg_name, alias={"td", "删除", "取消订阅"}),
        Subcommand("list", alias={"列表", "订阅列表"}),
        Subcommand("liveon", arg_name, alias={"开启直播"}),
        Subcommand("liveoff", arg_name, alias={"关闭直播"}),
        Subcommand("dynon", arg_name, alias={"开启动态"}),
        Subcommand("dynoff", arg_name, alias={"关闭动态"}),
        Subcommand("recon", arg_name, alias={"开启录播"}),
        Subcommand("recoff", arg_name, alias={"关闭录播"}),
    ),
    aliases={"B站直播间订阅", "b站直播间订阅"},
    use_cmd_start=True,
    block=True,
    priority=12,
)


async def find_user(matcher: Matcher, name: str) -> BiliUser:
    user = None
    if name.isdigit():
        uid = int(name)
        user = await get_user(uid)
        if not user:
            try:
                user = await get_user_info_by_uid(uid)
            except Exception:
                logger.warning(traceback.format_exc())
    else:
        users = await get_users()
        for sub_user in users:
            if sub_user.name == name:
                user = sub_user
        if not user:
            try:
                user = await get_user_info_by_name(name)
            except Exception:
                logger.warning(traceback.format_exc())

    if not user:
        await matcher.finish("获取用户信息失败，请检查名称或稍后再试")

    return user


@blive.assign("add")
async def _(matcher: Matcher, target: SaaTarget, name: str):
    user = await find_user(matcher, name)

    if await get_sub(target, user.uid):
        await blive.finish(f"{user.name} 已经订阅过了")

    await add_sub(Subscription(target=target, user=user, options=SubscriptionOptions()))

    await blive.finish(f"成功添加订阅 {user.name}")


@blive.assign("del")
async def _(matcher: Matcher, target: SaaTarget, name: str):
    user = await find_user(matcher, name)

    if not await get_sub(target, user.uid):
        await blive.finish(f"{user.name} 还没有订阅过")

    await del_sub(target, user.uid)

    await blive.finish(f"成功取消订阅 {user.name}")


@blive.assign("list")
async def _(matcher: Matcher, target: SaaTarget):
    subs = await get_subs(target)
    if not subs:
        await matcher.finish("目前还没有任何订阅")

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
    await matcher.finish(msg)


@blive.assign("liveon")
async def _(matcher: Matcher, target: SaaTarget, name: str):
    user = await find_user(matcher, name)

    if not (sub := await get_sub(target, user.uid)):
        await matcher.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.live = True
    await update_sub_options(target, user.uid, options)

    await matcher.finish(f"{user.name} 直播推送已打开")


@blive.assign("liveoff")
async def _(matcher: Matcher, target: SaaTarget, name: str):
    user = await find_user(matcher, name)

    if not (sub := await get_sub(target, user.uid)):
        await matcher.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.live = False
    await update_sub_options(target, user.uid, options)

    await matcher.finish(f"{user.name} 直播推送已关闭")


@blive.assign("dynon")
async def _(matcher: Matcher, target: SaaTarget, name: str):
    user = await find_user(matcher, name)

    if not (sub := await get_sub(target, user.uid)):
        await matcher.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.dynamic = True
    await update_sub_options(target, user.uid, options)

    await matcher.finish(f"{user.name} 动态推送已打开")


@blive.assign("dynoff")
async def _(matcher: Matcher, target: SaaTarget, name: str):
    user = await find_user(matcher, name)

    if not (sub := await get_sub(target, user.uid)):
        await matcher.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.dynamic = False
    await update_sub_options(target, user.uid, options)

    await matcher.finish(f"{user.name} 动态推送已关闭")


@blive.assign("recon")
async def _(matcher: Matcher, target: SaaTarget, name: str):
    user = await find_user(matcher, name)

    if not (sub := await get_sub(target, user.uid)):
        await matcher.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.record = True
    await update_sub_options(target, user.uid, options)

    await matcher.send(f"{user.name} 自动录播已打开")
    await sync_tasks()


@blive.assign("recoff")
async def _(matcher: Matcher, target: SaaTarget, name: str):
    user = await find_user(matcher, name)

    if not (sub := await get_sub(target, user.uid)):
        await matcher.finish(f"{user.name} 还没有订阅过")

    options = sub.options
    options.record = False
    await update_sub_options(target, user.uid, options)

    await matcher.send(f"{user.name} 自动录播已关闭")
    await sync_tasks()
