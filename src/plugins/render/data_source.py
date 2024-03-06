from pathlib import Path

import jinja2
from nonebot_plugin_htmlrender import md_to_pic, text_to_pic

dir_path = Path(__file__).parent
tpl_path = dir_path / "template"

env = jinja2.Environment(loader=jinja2.FileSystemLoader(tpl_path), enable_async=True)


async def t2p(text: str) -> bytes:
    return await text_to_pic(text, css_path=str(tpl_path / "text.css"), width=10)


async def m2p(text: str) -> bytes:
    return await md_to_pic(text)
