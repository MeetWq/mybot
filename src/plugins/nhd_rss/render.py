from pathlib import Path
from typing import Optional

import jinja2
from nonebot.log import logger
from nonebot_plugin_htmlrender import html_to_pic

from .data_source import NHDRSSEntry

dir_path = Path(__file__).parent
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)


async def rss_to_image(rss: NHDRSSEntry) -> Optional[bytes]:
    try:
        template = env.get_template(f"nhd.html")
        html = await template.render_async(rss=rss)
        return await html_to_pic(
            html,
            viewport={"width": 300, "height": 100},
            template_path=f"file://{template_path.absolute()}",
        )
    except Exception as e:
        logger.warning(f"Error in get_rss_entries: {e}")
