import jinja2
from typing import List
from pathlib import Path
from nonebot.log import logger
from nonebot_plugin_htmlrender import html_to_pic
from nonebot.adapters.cqhttp import Event, GroupMessageEvent

from .plugin import PluginInfo

dir_path = Path(__file__).parent
template_path = dir_path / 'template'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                         enable_async=True)


async def get_help_img(event: Event, plugins: List[PluginInfo]) -> bytes:
    try:
        template = env.get_template('help.html')
        type = 'group' if isinstance(event, GroupMessageEvent) else 'private'
        content = await template.render_async(type=type, plugins=plugins)
        return await html_to_pic(content, wait=0, viewport={"width": 100, "height": 100})
    except Exception as e:
        logger.warning(f"Error in get_help_img: {e}")
        return None


async def get_plugin_img(plugin: PluginInfo) -> bytes:
    try:
        template = env.get_template('plugin.html')
        content = await template.render_async(plugin=plugin)
        return await html_to_pic(content, wait=0, viewport={"width": 500, "height": 100})
    except Exception as e:
        logger.warning(f"Error in get_plugin_img({plugin.name}): {e}")
        return None
