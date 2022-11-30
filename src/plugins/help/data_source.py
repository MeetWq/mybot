import jinja2
from typing import List, Optional
from pathlib import Path
from nonebot.log import logger
from nonebot_plugin_htmlrender import html_to_pic

from .plugin import PluginInfo

dir_path = Path(__file__).parent
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)


async def get_help_img(event_type: str, plugins: List[PluginInfo]) -> Optional[bytes]:
    try:
        template = env.get_template("help.html")
        content = await template.render_async(type=event_type, plugins=plugins)
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
