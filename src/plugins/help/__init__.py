from nonebot import on_command
from nonebot.plugin import get_loaded_plugins
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent

from nonebot_plugin_manager import PluginManager


help = on_command('help', aliases={'帮助'}, priority=11)


@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    plugin_name = str(event.get_message()).strip()
    help_msg = ''
    if plugin_name:
        help_msg = await get_help_msg(event, plugin_name)
    else:
        if event.is_tome():
            help_msg = await get_help_msg(event)
    if help_msg:
        await help.finish(help_msg)


async def get_help_msg(event: Event, plugin_name=''):
    plugins = list(filter(
        lambda p: set(p.export.keys()).issuperset({'description', 'help'}), get_loaded_plugins()
    ))

    conv = {
        "user": [event.user_id] if not isinstance(event, GroupMessageEvent) else [],
        "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
    }
    plugin_manager = PluginManager()
    plugin = plugin_manager.get_plugin(conv, 1)
    plugins = [p for p in plugins if plugin[p.name]]

    if not plugins:
        return '暂时没有可用的功能'

    plugins.sort(key=lambda p: p.name)

    if not plugin_name:
        plugins_list = '\n'.join(p.name + ': ' + p.export.description for p in plugins)
        msg = '我现在的功能有: \n\n' + plugins_list + '\n\n发送 "help [名称]" 查看详情\n管理员可以通过 "npm block/unblock {名称}" 管理插件'
        return msg
    else:
        for p in plugins:
            if plugin_name.lower() == p.name or  plugin_name.lower() == p.export.description.lower():
                return p.export.help
        return ''
