import json
from pathlib import Path
from typing import List, Any
from pydantic import BaseModel, ValidationError
from nonebot import get_driver
from nonebot.plugin import Plugin, get_loaded_plugins
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from nonebot_plugin_manager import PluginManager


info_path = Path("data/help/info.json")


class PluginInfo(BaseModel):
    name: str
    short_name: str = ""
    description: str = ""
    command: str = ""
    short_command: str = ""
    example: str = ""
    notice: str = ""
    usage: str = ""
    status: bool = True
    locked: bool = False

    def __eq__(self, other: "PluginInfo"):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def load_plugin_info() -> List[PluginInfo]:
    if not info_path.exists():
        return []
    infos = []
    with info_path.open("r", encoding="utf8") as fp:
        data = json.load(fp)
    for p in data["plugins"]:
        try:
            infos.append(PluginInfo.parse_obj(p))
        except ValidationError:
            pass
    return sorted(infos, key=lambda i: i.short_name or i.name)


def dump_plugin_info(infos: List[PluginInfo]):
    info_path.parent.mkdir(parents=True, exist_ok=True)
    infos_dict = {
        "plugins": [info.dict(exclude={"status", "locked"}) for info in infos]
    }
    with info_path.open("w", encoding="utf8") as fp:
        json.dump(
            infos_dict,
            fp,
            indent=4,
            ensure_ascii=False,
        )


driver = get_driver()


@driver.on_startup
def update_plugin_info():
    plugins = get_loaded_plugins()
    infos = []
    for p in plugins:
        infos.append(
            PluginInfo(
                name=p.name,
                short_name=get_plugin_attr(p, "__help__plugin_name__"),
                description=get_plugin_attr(p, "__des__"),
                command=get_plugin_attr(p, "__cmd__"),
                short_command=get_plugin_attr(p, "__short_cmd__"),
                example=get_plugin_attr(p, "__example__"),
                notice=get_plugin_attr(p, "__notice__"),
                usage=get_plugin_attr(p, "__usage__"),
            )
        )
    loaded_infos = set(load_plugin_info())
    for info in infos:
        loaded_infos.add(info)
    dump_plugin_info(list(loaded_infos))


def get_plugin_attr(plugin: Plugin, attr: str):
    try:
        return plugin.module.__getattribute__(attr)
    except:
        return ""


def get_plugins(event: MessageEvent) -> List[PluginInfo]:
    infos = load_plugin_info()
    conv = {
        "user": [event.user_id],
        "group": [event.group_id] if isinstance(event, GroupMessageEvent) else [],
    }
    plugin_manager = PluginManager()
    plugins_read = plugin_manager.get_plugin(conv, 4)
    plugins_write = plugin_manager.get_plugin(conv, 2)
    plugins_exec = plugin_manager.get_plugin(conv, 1)
    plugins = []
    for info in infos:
        if plugins_read.get(info.name, False):
            info.status = plugins_exec.get(info.name, False)
            info.locked = not plugins_write.get(info.name, False)
            if not info.short_command:
                info.short_command = f"发送 help {info.short_name or info.name} 查看详情"
            plugins.append(info)
    return plugins
