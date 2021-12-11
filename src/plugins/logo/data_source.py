import base64
import jinja2
import imageio
from PIL import Image
from lxml import etree
from io import BytesIO
from pathlib import Path
from typing import List, Union

from nonebot.log import logger
from src.libs.playwright import get_new_page

dir_path = Path(__file__).parent
template_path = dir_path / 'template'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                         enable_async=True)


async def create_pornhub_logo(left_text, right_text):
    template = env.get_template('pornhub.html')
    content = await template.render_async(left_text=left_text, right_text=right_text)

    async with get_new_page(viewport={"width": 100, "height": 100}) as page:
        await page.set_content(content)
        img = await page.screenshot(full_page=True)
    return img


async def create_youtube_logo(left_text, right_text):
    template = env.get_template('youtube.html')
    content = await template.render_async(left_text=left_text, right_text=right_text)

    async with get_new_page(viewport={"width": 100, "height": 100}) as page:
        await page.set_content(content)
        img = await page.screenshot(full_page=True)
    return img


async def create_5000choyen_logo(top_text, bottom_text):
    template = env.get_template('5000choyen.html')
    top_text = top_text.replace('！', '!').replace('？', '?')
    bottom_text = bottom_text.replace('！', '!').replace('？', '?')
    content = await template.render_async(top_text=top_text, bottom_text=bottom_text)

    async with get_new_page() as page:
        await page.set_content(content)
        a = await page.query_selector('a')
        img = await (await a.get_property('href')).json_value()
    return 'base64://' + img.replace('data:image/png;base64,', '')


async def create_douyin_logo(text):
    template = env.get_template('douyin.html')
    content = await template.render_async(text=text)

    async with get_new_page() as page:
        await page.set_content(content)
        content = await page.content()

    dom = etree.HTML(content)
    imgs = dom.xpath('//a/@href')
    imgs = [Image.open(BytesIO(base64.b64decode(
        img.replace('data:image/png;base64,', '')))) for img in imgs]

    output = BytesIO()
    imageio.mimsave(output, imgs, format='gif', duration=0.2)
    return output


commands = {
    'pornhub': {
        'aliases': {'ph ', 'phlogo'},
        'func': create_pornhub_logo,
        'arg_num': 2
    },
    'youtube': {
        'aliases': {'yt ', 'ytlogo'},
        'func': create_youtube_logo,
        'arg_num': 2
    },
    '5000choyen': {
        'aliases': {'5000兆', '5000choyen'},
        'func': create_5000choyen_logo,
        'arg_num': 2
    },
    'douyin': {
        'aliases': {'douyin'},
        'func': create_douyin_logo,
        'arg_num': 1
    }
}


async def create_logo(texts: List[str], style: str) -> Union[str, bytes, BytesIO, Path]:
    try:
        func = commands[style]['func']
        return await func(*texts)
    except Exception as e:
        logger.warning(
            f"Error in create_logo({', '.join(texts)}, {style}): {e}")
        return None
