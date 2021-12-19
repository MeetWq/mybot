from nonebot.plugin import Plugin, get_loaded_plugins
from nonebot.adapters.cqhttp import Event

from nonebot_plugin_manager import PluginManager


class PluginInfo:
    def __init__(self, plugin: Plugin):
        self.name = plugin.name
        short_name = get_plugin_attr(plugin, '__help__plugin_name__')
        if not short_name:
            short_name = self.name
        self.short_name = short_name
        self.description = get_plugin_attr(plugin, '__des__')
        self.command = get_plugin_attr(plugin, '__cmd__')
        self.usage = get_plugin_attr(plugin, '__usage__')
        short_command = get_plugin_attr(plugin, '__short_cmd__')
        if not short_command:
            short_command = f'发送 "help {self.short_name}" 查看详情' if self.usage else ''
        self.short_command = short_command
        self.example = get_plugin_attr(plugin, '__example__')
        self.notice = get_plugin_attr(plugin, '__notice__')
        self.status = True
        self.locked = False


def get_plugin_attr(plugin: Plugin, attr: str):
    try:
        return plugin.module.__getattribute__(attr)
    except:
        return ''


def get_plugins(event: Event):
    plugins = [PluginInfo(p) for p in get_loaded_plugins()]
    conv = {
        "user": [event.user_id] if hasattr(event, "user_id") else [],
        "group": [event.group_id] if hasattr(event, "group_id") else []
    }
    plugin_manager = PluginManager()
    plugins_read = plugin_manager.get_plugin(conv, 4)
    plugins = [p for p in plugins if plugins_read.get(p.name, False)]

    plugins_write = plugin_manager.get_plugin(conv, 2)
    plugins_exec = plugin_manager.get_plugin(conv, 1)
    for p in plugins:
        p.locked = not plugins_write.get(p.name, False)
        p.status = plugins_exec.get(p.name, False)

    plugins.sort(key=lambda p: p.short_name)
    return plugins
