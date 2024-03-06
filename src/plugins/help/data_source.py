from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import jinja2
from nonebot import get_plugin
from nonebot.log import logger
from nonebot_plugin_htmlrender import html_to_pic

from src.utils.plugin_manager import plugin_manager

dir_path = Path(__file__).parent
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)


@dataclass
class PluginInfo:
    package_name: str
    name: str = ""
    description: str = ""
    usage: str = ""
    extra: Dict[Any, Any] = field(default_factory=dict)
    enabled: bool = True
    locked: bool = False


def get_plugin_info(user_id: str, plugin_name: str) -> Optional[PluginInfo]:
    plugin = get_plugin(plugin_name)
    if not plugin:
        return
    info = PluginInfo(package_name=plugin.name)
    if metadata := plugin.metadata:
        info.name = metadata.name
        info.description = metadata.description
        info.usage = metadata.usage
        info.extra.update(metadata.extra)
    if plugin_config := plugin_manager.get_config(plugin.name):
        info.enabled = plugin_manager.check(plugin.name, user_id)
        info.locked = not bool(plugin_config.mode & 2)
    return info


async def get_help_img(plugins: List[PluginInfo]) -> Optional[bytes]:
    try:
        template = env.get_template("help.html")
        content = await template.render_async(plugins=plugins)
        return await html_to_pic(
            content,
            wait=0,
            viewport={"width": 100, "height": 100},
            template_path=f"file://{template_path.absolute()}",
        )
    except Exception as e:
        logger.warning(f"Error in get_help_img: {e}")
        return None


async def get_plugin_img(plugin: PluginInfo) -> Optional[bytes]:
    try:
        template = env.get_template("plugin.html")
        content = await template.render_async(plugin=plugin)
        return await html_to_pic(
            content,
            wait=0,
            viewport={"width": 500, "height": 100},
            template_path=f"file://{template_path.absolute()}",
        )
    except Exception as e:
        logger.warning(f"Error in get_plugin_img({plugin.package_name}): {e}")
        return None
