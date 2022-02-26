from argparse import Namespace
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
from .clipper import cut_start, cut_stop
from .blrec import sync_tasks
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


async def add_sub(args: Namespace):
    if res := add_sub_list(args.user_id, args.uid, args.info):
        await blive.finish(res)
    await sync_tasks()
    await blive.finish(f"成功订阅 {args.up_name} 的直播间")


async def del_sub(args: Namespace):
    if res := del_sub_list(args.user_id, args.uid):
        await blive.finish(res)
    await sync_tasks()
    await blive.finish(f"成功取消订阅 {args.up_name} 的直播间")


async def list_sub(args: Namespace):
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


async def clear_sub(args: Namespace):
    clear_sub_list(args.user_id)
    await sync_tasks()
    await blive.finish("订阅列表已清空")


async def dynon(args: Namespace):
    if res := open_dynamic(args.user_id, args.uid):
        await blive.finish(res)
    await blive.finish(f"{args.up_name} 动态推送已打开")


async def dynoff(args: Namespace):
    if res := close_dynamic(args.user_id, args.uid):
        await blive.finish(res)
    await blive.finish(f"{args.up_name} 动态推送已关闭")


async def recon(args: Namespace):
    if res := open_record(args.user_id, args.uid):
        await blive.finish(res)
    await sync_tasks()
    await blive.finish(f"{args.up_name} 自动录播已打开")


async def recoff(args: Namespace):
    if res := close_record(args.user_id, args.uid):
        await blive.finish(res)
    await sync_tasks()
    await blive.finish(f"{args.up_name} 自动录播已关闭")


async def cuton(args: Namespace):
    if res := await cut_start(args.user_id, args.uid, float(args.offset)):
        await blive.finish(res)


async def cutoff(args: Namespace):
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
async def _(args: Namespace = ShellCommandArgs(), user_id: str = Depends(get_id)):
    args.user_id = user_id

    if hasattr(args, "name"):
        name = str(args.name)
        if name.isdigit():
            info = await get_live_info(uid=name)
        else:
            info = await get_live_info(up_name=name)
        if not info:
            await blive.finish("获取直播间信息失败，请检查名称或稍后再试")
        args.uid = str(info["uid"])
        args.up_name = info["uname"]
        args.info = info

    if hasattr(args, "func"):
        await args.func(args)
