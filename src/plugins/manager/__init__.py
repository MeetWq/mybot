from typing import Dict, List
from nonebot import on_command
from nonebot.rule import Rule
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent, Message

from nonebot_plugin_manager import PluginManager
from ..help.plugin import get_plugins


__des__ = "插件管理"
__cmd__ = """
启用/禁用 {plugin}
""".strip()
__short_cmd__ = __cmd__
__example__ = """
禁用 setu
""".strip()
__notice__ = "此功能仅群管理员或超级用户可用"
__usage__ = (
    f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}\nNotice:\n{__notice__}"
)


def manager_rule(bot: Bot, event: MessageEvent) -> bool:
    return isinstance(event, GroupMessageEvent) and (
        str(event.user_id) in bot.config.superusers
        or event.sender.role in ["admin", "owner"]
    )


block = on_command("禁用", block=True, rule=Rule(manager_rule))
unblock = on_command("启用", block=True, rule=Rule(manager_rule))

Conv = Dict[str, List[int]]


def get_conv(event: MessageEvent) -> Conv:
    return {
        "user": [event.user_id],
        "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
    }


@block.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugins = get_plugins(event)
    plugin = None
    for p in plugins[::-1]:
        if keyword.lower() in (p.name.lower(), p.short_name.lower()):
            plugin = p
            break
    if not plugin:
        await block.finish(f"插件 {keyword} 不存在！")

    plugin_manager = PluginManager()
    conv: Conv = get_conv(event)
    if conv["group"]:
        conv["user"] = []
    result = plugin_manager.block_plugin([plugin.name], conv)
    if result.get(plugin.name, False):
        res = f"插件 {plugin.short_name or plugin.name} 禁用成功"
    else:
        res = f"插件 {plugin.short_name or plugin.name} 不存在或已关闭编辑权限！"
    await block.finish(res)


@unblock.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        return

    plugins = get_plugins(event)
    plugin = None
    for p in plugins[::-1]:
        if keyword.lower() in (p.name.lower(), p.short_name.lower()):
            plugin = p
            break
    if not plugin:
        await unblock.finish(f"插件 {keyword} 不存在！")

    plugin_manager = PluginManager()
    conv: Conv = get_conv(event)
    if conv["group"]:
        conv["user"] = []
    result = plugin_manager.unblock_plugin([plugin.name], conv)
    if result.get(plugin.name, False):
        res = f"插件 {plugin.short_name or plugin.name} 启用成功"
    else:
        res = f"插件 {plugin.short_name or plugin.name} 不存在或已关闭编辑权限！"
    await unblock.finish(res)
