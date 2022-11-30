from typing import Dict, List

from nonebot.rule import Rule
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, Message

from nonebot_plugin_manager import PluginManager

from ..help.plugin import get_plugins

__plugin_meta__ = PluginMetadata(
    name="插件管理",
    description="启用/禁用插件",
    usage="启用插件/插件 插件名",
    extra={
        "example": "禁用插件 setu",
        "notice": "仅群管理员或超级用户可用",
    },
)


def manager_rule(bot: Bot, event: MessageEvent) -> bool:
    return isinstance(event, GroupMessageEvent) and (
        str(event.user_id) in bot.config.superusers
        or event.sender.role in ["admin", "owner"]
    )


block = on_command("禁用插件", block=True, rule=Rule(manager_rule))
unblock = on_command("启用插件", block=True, rule=Rule(manager_rule))

Conv = Dict[str, List[int]]


def get_conv(event: MessageEvent) -> Conv:
    return {
        "user": [event.user_id],
        "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
    }


@block.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugins = get_plugins(event)
    plugin = None
    for p in plugins[::-1]:
        if keyword.lower() in (
            p.package_name.lower(),
            p.name.lower(),
            p.extra.get("unique_name", "_").lower(),
        ):
            plugin = p
            break
    if not plugin:
        await block.finish(f"插件 {keyword} 不存在！")

    plugin_manager = PluginManager()
    conv: Conv = get_conv(event)
    if str(event.user_id) in bot.config.superusers:
        plugins_write = plugin_manager.get_plugin(perm=2)
    else:
        plugins_write = plugin_manager.get_plugin(conv, 2)
    if plugin.package_name not in plugins_write:
        await block.finish(f"插件 {plugin.name} 已关闭编辑权限！")

    if conv["group"]:
        conv["user"] = []
    result = plugin_manager.block_plugin([plugin.name], conv)
    if result.get(plugin.name, False):
        res = f"插件 {plugin.name} 禁用成功"
    else:
        res = f"插件 {plugin.name} 不存在或已关闭编辑权限！"
    await block.finish(res)


@unblock.handle()
async def _(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugins = get_plugins(event)
    plugin = None
    for p in plugins[::-1]:
        if keyword.lower() in (
            p.package_name.lower(),
            p.name.lower(),
            p.extra.get("unique_name", "_").lower(),
        ):
            plugin = p
            break
    if not plugin:
        await unblock.finish(f"插件 {keyword} 不存在！")

    plugin_manager = PluginManager()
    conv: Conv = get_conv(event)
    if str(event.user_id) in bot.config.superusers:
        plugins_write = plugin_manager.get_plugin(perm=2)
    else:
        plugins_write = plugin_manager.get_plugin(conv, 2)
    if plugin.package_name not in plugins_write:
        await unblock.finish(f"插件 {plugin.name} 已关闭编辑权限！")

    if conv["group"]:
        conv["user"] = []
    result = plugin_manager.unblock_plugin([plugin.name], conv)
    if result.get(plugin.name, False):
        res = f"插件 {plugin.name} 启用成功"
    else:
        res = f"插件 {plugin.name} 不存在或已关闭编辑权限！"
    await unblock.finish(res)
