from typing import Dict, List
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.plugin import Plugin, get_loaded_plugins
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent

from nonebot_plugin_manager import PluginManager

Conv = Dict[str, List[int]]


__des__ = '插件管理'
__cmd__ = '''
@我 启用/禁用 {plugin}
'''.strip()
__short_cmd__ = __cmd__
__example__ = '''
@小Q 禁用 setu
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


async def manager_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return (
        isinstance(event, GroupMessageEvent)
        and event.is_tome()
        and (
            str(event.user_id) in bot.config.superusers
            or event.sender.role in ['admin', 'owner']
        )
    )


block = on_command('block', rule=manager_rule, aliases={'禁用'})
unblock = on_command('unblock',  rule=manager_rule, aliases={'启用'})


@block.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = event.get_plaintext().strip()
    if not keyword:
        return
    conv = get_conv(event)
    plugin_name, short_name = get_plugin_name(conv, keyword)
    if not plugin_name:
        await block.finish(f'插件 {keyword} 不存在!')
    plugin_manager = PluginManager()
    if conv["group"]:
        conv["user"] = []
    result = plugin_manager.block_plugin([plugin_name], conv)
    if result.get(plugin_name, False):
        msg = f'插件 {short_name} 禁用成功'
    else:
        msg = f'插件 {short_name} 不存在或已关闭编辑权限！'
    await block.finish(msg)


@unblock.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = event.get_plaintext().strip()
    if not keyword:
        return
    conv = get_conv(event)
    plugin_name, short_name = get_plugin_name(conv, keyword)
    if not plugin_name:
        await unblock.finish(f'插件 {keyword} 不存在！')
    plugin_manager = PluginManager()
    if conv["group"]:
        conv["user"] = []
    result = plugin_manager.unblock_plugin([plugin_name], conv)
    if result.get(plugin_name, False):
        msg = f'插件 {short_name} 启用成功'
    else:
        msg = f'插件 {short_name} 不存在或已关闭编辑权限！'
    await unblock.finish(msg)


def get_plugin_attr(plugin: Plugin, attr: str):
    try:
        return plugin.module.__getattribute__(attr)
    except:
        return ''


def get_conv(event: Event):
    return {
        "user": [event.user_id] if hasattr(event, "user_id") else [],
        "group": [event.group_id] if hasattr(event, "group_id") else []
    }


def get_plugin_name(conv: Conv, name: str):
    plugins = get_loaded_plugins()
    plugin_manager = PluginManager()
    plugins_read = plugin_manager.get_plugin(conv, 4)
    plugins = [p for p in plugins if plugins_read.get(p.name, False)]
    for p in plugins:
        short_name = get_plugin_attr(p, '__help__plugin_name__')
        if not short_name:
            short_name = p.name
        if name.lower() in (p.name.lower(), short_name.lower()):
            return p.name, short_name
    return '', ''
