import jinja2
from typing import List
from pathlib import Path
from src.libs.playwright import get_new_page
from nonebot.log import logger
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
        with open('result.html', 'w') as f:
            f.write(content)

        async with get_new_page(viewport={"width": 100, "height": 100}) as page:
            await page.set_content(content)
            return await page.screenshot(full_page=True)
    except Exception as e:
        logger.warning(f"Error in get_help_img: {e}")
        return None
