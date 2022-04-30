from typing import List
from argparse import Namespace
from nonebot.matcher import Matcher
from nonebot import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.params import ShellCommandArgs, Depends
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from .monitor import *
from .rss_class import RSS
from .data_source import update_rss_info
from .rss_list import (
    get_rss_list,
    clear_rss_list,
    add_rss_list,
    del_rss_list,
    DupeError,
)


__des__ = "RSS订阅"
__cmd__ = """
添加订阅：rss add {订阅名} {RSSHub路径/完整URL}
取消订阅：rss del {订阅名}
订阅列表：rss list
清空订阅：rss clear
""".strip()
__example__ = """
rss add 订阅1 /bilibili/user/dynamic/282994
rss add 订阅2 https://rsshub.app/bilibili/user/dynamic/282994
""".strip()
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"


async def add_rss(matcher: Matcher, user_id: str, name: str, url: str, **kwargs):
    new_rss = RSS(name, url)
    status = await update_rss_info(new_rss)
    if not status:
        await matcher.finish("获取RSS信息失败，请检查链接或稍后再试")
    try:
        add_rss_list(user_id, new_rss)
    except DupeError:
        await matcher.finish("已存在该名称的订阅，请更换名称或删除之前的订阅")
    await matcher.finish(f"成功添加订阅 {name}：{new_rss.title}")


async def del_rss(matcher: Matcher, user_id: str, name: str, **kwargs):
    try:
        del_rss_list(user_id, name)
    except DupeError:
        await matcher.finish("不存在该名称的订阅")
    await matcher.finish(f"成功删除订阅 {name}")


async def list_rss(matcher: Matcher, user_id: str, **kwargs):
    rss_list: List[RSS] = get_rss_list(user_id)
    if not rss_list:
        await matcher.finish("目前还没有任何订阅")
    msg = "已订阅以下内容:\n"
    for r in rss_list:
        msg += f"\n{r.name} ({r.url})"
    await matcher.finish(msg)


async def clear_rss(matcher: Matcher, user_id: str, **kwargs):
    clear_rss_list(user_id)
    await matcher.finish("订阅列表已清空")


rss_parser = ArgumentParser("rss")

rss_subparsers = rss_parser.add_subparsers()

add_parser = rss_subparsers.add_parser("add", aliases=("添加"))
add_parser.add_argument("name")
add_parser.add_argument("url")
add_parser.set_defaults(func=add_rss)

del_parser = rss_subparsers.add_parser("del", aliases=("删除"))
del_parser.add_argument("name")
del_parser.set_defaults(func=del_rss)

list_parser = rss_subparsers.add_parser("list", aliases=("列表"))
list_parser.set_defaults(func=list_rss)

clear_parser = rss_subparsers.add_parser("clear", aliases=("清空"))
clear_parser.set_defaults(func=clear_rss)

rss = on_shell_command("rss", parser=rss_parser, block=True, priority=12)


def get_id(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return "group_" + str(event.group_id)
    else:
        return "private_" + str(event.user_id)


@rss.handle()
async def _(args: Namespace = ShellCommandArgs(), user_id: str = Depends(get_id)):
    args.matcher = rss
    args.user_id = user_id
    if hasattr(args, "func"):
        await args.func(**vars(args))
