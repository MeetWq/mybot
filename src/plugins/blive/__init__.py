from typing import Protocol
from argparse import Namespace
from dataclasses import dataclass
from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.params import ShellCommandArgs, Depends
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from .monitor import scheduler
from .data_source import get_live_info
from .sub_list import (
    get_sub_list,
    clear_sub_list,
    add_sub_list,
    del_sub_list,
    open_record,
    close_record,
    open_dynamic,
    close_dynamic,
)
from .blrec import sync_tasks
from .cutter import cut_start, cut_stop
from .uid_list import get_sub_info_by_uid, get_sub_info_by_name
from .server import blrec_handler, blrec_error_handler, uploader_handler


__des__ = "B站直播、动态订阅"
__cmd__ = """
添加订阅：blive d {用户名/UID}
取消订阅：blive td {用户名/UID}
订阅列表：blive list
清空订阅：blive clear
开启动态：blive dynon {用户名/UID}
关闭动态：blive dynoff {用户名/UID}
开启录播：blive recon {用户名/UID}
关闭录播：blive recoff {用户名/UID}
开始切片：blive cuton {用户名/UID} [偏移量]
结束切片：blive cutoff {用户名/UID} [偏移量]
""".strip()
__example__ = """
blive d 282994
blive d 泠鸢yousa
blive recon 泠鸢yousa
blive cuton 泠鸢yousa 60
blive cutoff 泠鸢yousa
""".strip()
__notice__ = "注意是UID不是房间号\n偏移量只能是正数，指前向偏移，单位为秒"
__usage__ = (
    f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}\nNotice:\n{__notice__}"
)


class Func(Protocol):
    async def __call__(self, args: "Args"):
        ...


@dataclass
class Args:
    user_id: str
    func: Func
    uid: str = ""
    up_name: str = ""
    room_id: str = ""
    offset: float = 0


async def add_sub(args: Args):
    if res := add_sub_list(args.user_id, args.uid, args.up_name, args.room_id):
        await blive.finish(res)
    await sync_tasks()
    await blive.finish(f"成功订阅 {args.up_name} 的直播间")


async def del_sub(args: Args):
    if res := del_sub_list(args.user_id, args.uid):
        await blive.finish(res)
    await sync_tasks()
    await blive.finish(f"成功取消订阅 {args.up_name} 的直播间")


async def list_sub(args: Args):
    sub_list = get_sub_list(args.user_id)
    if not sub_list:
        await blive.finish("目前还没有任何订阅")
    msg = "已订阅以下直播间:\n"
    for _, info in sub_list.items():
        record = info.get("record", False)
        dynamic = info.get("dynamic", False)
        msg += (
            f"\n{info['up_name']}{'（动态）' if dynamic else ''}{'（录播）' if record else ''}"
        )
    await blive.finish(msg)


async def clear_sub(args: Args):
    clear_sub_list(args.user_id)
    await sync_tasks()
    await blive.finish("订阅列表已清空")


async def dynon(args: Args):
    if res := open_dynamic(args.user_id, args.uid):
        await blive.finish(res)
    await blive.finish(f"{args.up_name} 动态推送已打开")


async def dynoff(args: Args):
    if res := close_dynamic(args.user_id, args.uid):
        await blive.finish(res)
    await blive.finish(f"{args.up_name} 动态推送已关闭")


async def recon(args: Args):
    if res := open_record(args.user_id, args.uid):
        await blive.finish(res)
    await sync_tasks()
    await blive.finish(f"{args.up_name} 自动录播已打开")


async def recoff(args: Args):
    if res := close_record(args.user_id, args.uid):
        await blive.finish(res)
    await sync_tasks()
    await blive.finish(f"{args.up_name} 自动录播已关闭")


async def cuton(args: Args):
    if res := await cut_start(args.user_id, args.uid, float(args.offset)):
        await blive.finish(res)


async def cutoff(args: Args):
    if res := await cut_stop(args.user_id, args.uid, float(args.offset)):
        await blive.finish(res)


blive_parser = ArgumentParser("blive")

blive_subparsers = blive_parser.add_subparsers()

add_parser = blive_subparsers.add_parser("add", aliases=("d", "添加", "添加订阅"))
add_parser.add_argument("name")
add_parser.set_defaults(func=add_sub)

del_parser = blive_subparsers.add_parser("del", aliases=("td", "删除", "取消订阅"))
del_parser.add_argument("name")
del_parser.set_defaults(func=del_sub)

list_parser = blive_subparsers.add_parser("list", aliases=("列表", "订阅列表"))
list_parser.set_defaults(func=list_sub)

clear_parser = blive_subparsers.add_parser("clear", aliases=("清空", "清空订阅"))
clear_parser.set_defaults(func=clear_sub)

dynon_parser = blive_subparsers.add_parser("dynon", aliases=("开启动态"))
dynon_parser.add_argument("name")
dynon_parser.set_defaults(func=dynon)

dynoff_parser = blive_subparsers.add_parser("dynoff", aliases=("关闭动态"))
dynoff_parser.add_argument("name")
dynoff_parser.set_defaults(func=dynoff)

recon_parser = blive_subparsers.add_parser("recon", aliases=("开启录播"))
recon_parser.add_argument("name")
recon_parser.set_defaults(func=recon)

recoff_parser = blive_subparsers.add_parser("recoff", aliases=("关闭录播"))
recoff_parser.add_argument("name")
recoff_parser.set_defaults(func=recoff)

cuton_parser = blive_subparsers.add_parser("cuton", aliases=("开始切片"))
cuton_parser.add_argument("name")
cuton_parser.add_argument("offset", type=float, nargs="?", default=0)
cuton_parser.set_defaults(func=cuton)

cutoff_parser = blive_subparsers.add_parser("cutoff", aliases=("结束切片"))
cutoff_parser.add_argument("name")
cutoff_parser.add_argument("offset", type=float, nargs="?", default=0)
cutoff_parser.set_defaults(func=cutoff)


blive = on_shell_command(
    "blive",
    aliases={"bilibili_live", "B站直播间", "b站直播间"},
    block=True,
    parser=blive_parser,
    priority=12,
)


def get_id(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return "group_" + str(event.group_id)
    else:
        return "private_" + str(event.user_id)


@blive.handle()
async def _(ns: Namespace = ShellCommandArgs(), user_id: str = Depends(get_id)):
    args = Args(user_id, ns.func)

    if hasattr(ns, "name"):
        name = str(ns.name)
        if name.isdigit():
            args.uid = name
            if info := get_sub_info_by_uid(name):
                args.up_name = info["up_name"]
                args.room_id = info["room_id"]
            elif info := await get_live_info(uid=name):
                args.up_name = info["uname"]
                args.room_id = str(info["room_id"])
            else:
                await blive.finish("获取直播间信息失败，请检查名称或稍后再试")
        else:
            args.up_name = name
            if info := get_sub_info_by_name(name):
                args.uid = info["uid"]
                args.room_id = info["room_id"]
            elif info := await get_live_info(up_name=name):
                args.uid = str(info["uid"])
                args.room_id = str(info["room_id"])
            else:
                await blive.finish("获取直播间信息失败，请检查名称或稍后再试")

    if hasattr(ns, "offset"):
        args.offset = ns.offset

    await args.func(args)
