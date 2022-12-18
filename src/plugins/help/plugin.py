import json
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel, ValidationError

from nonebot import get_driver
from nonebot.plugin import Plugin, get_loaded_plugins
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from nonebot_plugin_manager import PluginManager


info_path = Path("data/plugin_info.json")


class PluginInfo(BaseModel):
    package_name: str
    name: str = ""
    description: str = ""
    usage: str = ""
    extra: Dict[Any, Any] = {}
    enabled: bool = True
    locked: bool = False

    def __eq__(self, other: "PluginInfo"):
        return self.package_name == other.package_name

    def __hash__(self):
        return hash(self.package_name)


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
    return sorted(infos, key=lambda i: i.package_name)


def dump_plugin_info(infos: List[PluginInfo]):
    info_path.parent.mkdir(parents=True, exist_ok=True)
    infos_dict = {
        "plugins": [info.dict(exclude={"enabled", "locked"}) for info in infos]
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
    infos: List[PluginInfo] = []
    for p in plugins:
        info = PluginInfo(package_name=p.name)
        info.extra["unique_name"] = (
            p.name.replace("nonebot_plugin_", "")
            .replace("nonebot-plugin-", "")
            .replace("nonebot_", "")
            .replace("nonebot-", "")
        )
        if metadata := p.metadata:
            info.name = metadata.name
            info.description = metadata.description
            info.usage = metadata.usage
            info.extra.update(metadata.extra)
        else:
            info.name = get_plugin_attr(p, "__help__plugin_name__") or p.name
            info.description = get_plugin_attr(p, "__des__")
            info.usage = get_plugin_attr(p, "__usage__")
            info.extra["example"] = get_plugin_attr(p, "__example__")
            info.extra["notice"] = get_plugin_attr(p, "__notice__")
        if info.name and info.usage and info.description:
            infos.append(info)
    infos_set = set(infos)
    for info in load_plugin_info():
        infos_set.add(info)
    infos = list(infos_set)
    infos = sorted(infos, key=lambda i: i.package_name)
    dump_plugin_info(infos)


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
    plugins_write = plugin_manager.get_plugin(conv, 6)
    plugins_exec = plugin_manager.get_plugin(conv, 1)
    plugins: List[PluginInfo] = []
    for info in infos:
        if plugins_read.get(info.package_name, False):
            info.enabled = plugins_exec.get(info.package_name, False)
            info.locked = not plugins_write.get(info.package_name, False)
            plugins.append(info)
    return plugins
