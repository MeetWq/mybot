import io
import base64
import jinja2
import imageio
import traceback
from PIL import Image
from lxml import etree
from pathlib import Path

from nonebot.log import logger
from nonebot.adapters.cqhttp import MessageSegment
from src.libs.playwright import get_new_page

dir_path = Path(__file__).parent
template_path = dir_path / 'template'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                         enable_async=True)


async def create_logo(texts, style='pornhub'):
    try:
        if style == 'pornhub':
            image = await create_pornhub_logo(texts[0], texts[1])
        elif style == 'youtube':
            image = await create_youtube_logo(texts[0], texts[1])
        elif style == '5000choyen':
            image = await create_5000choyen_logo(texts[0], texts[1])
        elif style == 'douyin':
            image = await create_douyin_logo(' '.join(texts))

        if image:
            return MessageSegment.image(image)
        return None
    except (AttributeError, TypeError, OSError):
        logger.debug(traceback.format_exc())
        return None


def load_woff(name):
    with (template_path / name).open('rb') as f:
        return 'data:application/x-font-woff;charset=utf-8;base64,' + base64.b64encode(f.read()).decode()


def load_png(name):
    with (template_path / name).open('rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


def load_file(name):
    with (template_path / name).open('r', encoding='utf-8') as f:
        return f.read()


env.filters['load_woff'] = load_woff
env.filters['load_png'] = load_png
env.filters['load_file'] = load_file


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
        img = img.replace('data:image/png;base64,', '')
    return base64.b64decode(img)


async def create_douyin_logo(text):
    template = env.get_template('douyin.html')
    content = await template.render_async(text=text)

    async with get_new_page() as page:
        await page.set_content(content)
        content = await page.content()

    dom = etree.HTML(content)
    imgs = dom.xpath('//a/@href')
    imgs = [Image.open(io.BytesIO(base64.b64decode(
        img.replace('data:image/png;base64,', '')))) for img in imgs]

    output = io.BytesIO()
    imageio.mimsave(output, imgs, format='gif', duration=0.2)
    return output.getvalue()
