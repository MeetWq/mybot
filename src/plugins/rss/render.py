import re
import base64
import jinja2
import aiohttp
import mimetypes
from pathlib import Path
from nonebot import get_driver
from src.libs.playwright import get_new_page

from .rss_class import RSS

global_config = get_driver().config
proxy = global_config.http_proxy

dir_path = Path(__file__).parent
template_path = dir_path / 'template'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                         enable_async=True)


async def rss_to_image(rss: RSS, info: dict) -> bytearray:
    html = await rss_to_html(rss, info)
    html = await replace_url(html, rss.link)
    async with get_new_page(viewport={"width": 800, "height": 100}) as page:
        await page.set_content(html)
        img = await page.screenshot(type='jpeg', full_page=True)
    return img


async def rss_to_html(rss: RSS, info: dict) -> str:
    template = env.get_template('main.html')
    return await template.render_async(rss=rss, info=info)


async def replace_url(text: str, base_url: str) -> str:
    pattern = r'<img .*?src=[\"\'](.*?)[\"\'].*?/>'
    urls = re.findall(pattern, text, re.DOTALL)
    for url in urls:
        url_new = RSS.parse_url(url, base_url)
        b64 = await url_to_b64(url_new)
        text = text.replace(url, b64, 1)
    return text


async def url_to_b64(url: str) -> str:
    result = await download_img(url)
    if not result:
        return url
    type = mimetypes.guess_type(url)[0]
    if not type:
        type = 'image'
    return f'data:{type};base64,{base64.b64encode(result).decode()}'


async def download_img(url: str) -> bytearray:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy) as resp:
                result = await resp.read()
        return result
    except:
        return None
