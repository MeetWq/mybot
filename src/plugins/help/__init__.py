from typing import Annotated, Optional, Union

from nonebot import on_command, require
from nonebot.adapters import Event, Message
from nonebot.params import CommandArg, Depends
from nonebot.plugin import PluginMetadata, get_loaded_plugins

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_uninfo import Uninfo

from src.utils.plugin_manager import plugin_manager

from .data_source import get_help_img, get_plugin_img, get_plugin_info

__plugin_meta__ = PluginMetadata(
    name="帮助",
    description="查看插件帮助",
    usage='@我 发送 "help/帮助" 查看已加载插件\n发送 "help 插件名" 查看插件详情',
    extra={
        "example": "help help",
    },
)


def get_user_id(uninfo: Uninfo) -> str:
    return f"{uninfo.scope}_{uninfo.self_id}_{uninfo.scene_path}"


UserId = Annotated[str, Depends(get_user_id)]

help = on_command("help", aliases={"帮助", "功能"}, block=True)


@help.handle()
async def _(event: Event, user_id: UserId, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()

    help_msg = None
    if keyword:
        help_msg = await get_help_msg(user_id, keyword)
    elif event.is_tome():
        help_msg = await get_help_msg(user_id)
    if help_msg:
        if isinstance(help_msg, str):
            await help.finish(help_msg)
        else:
            await UniMessage.image(raw=help_msg).send()


async def get_help_msg(user_id: str, keyword: str = "") -> Optional[Union[str, bytes]]:
    def visible_plugin(plugin_name: str) -> bool:
        if plugin_config := plugin_manager.get_config(plugin_name):
            return bool(plugin_config.mode & 4)
        return False

    plugins = get_loaded_plugins()
    plugins = list(filter(lambda p: visible_plugin(p.name), plugins))

    if not keyword:
        if not plugins:
            return "暂时没有可用的功能"
        plugin_infos = []
        for plugin in plugins:
            if info := get_plugin_info(user_id, plugin.name):
                plugin_infos.append(info)
        if not plugin_infos:
            return "暂时没有可用的功能"
        plugin_infos = sorted(plugin_infos, key=lambda i: i.package_name)
        img = await get_help_img(plugin_infos)
        return img if img else "出错了，请稍后再试"
    else:
        plugin_name = plugin_manager.find(keyword)
        if (
            plugin_name
            and visible_plugin(plugin_name)
            and (info := get_plugin_info(user_id, plugin_name))
        ):
            img = await get_plugin_img(info)
            return img if img else "出错了，请稍后再试"
