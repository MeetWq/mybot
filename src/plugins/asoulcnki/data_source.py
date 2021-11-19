import json
import time
import base64
import jinja2
import aiohttp
import traceback
from pathlib import Path

from nonebot.log import logger
from nonebot.adapters.cqhttp import Message, MessageSegment
from src.libs.playwright import get_new_page

dir_path = Path(__file__).parent
template_path = dir_path / 'template'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                         enable_async=True)


async def check_text(text):
    try:
        url = 'https://asoulcnki.asia/v1/api/check'
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, data=json.dumps({'text': text})) as resp:
                result = await resp.json()
        code = result['code']
        if code != 0:
            return None
        data = result['data']
        rate = data['rate']
        if not data['related']:
            return '没有找到重复的小作文捏'
        related = data['related'][0]
        reply_url = related['reply_url'].strip()
        reply = related['reply']
        username = reply['m_name']
        content = reply['content']
        ctime = reply['ctime']

        msg = Message()
        msg.append('总复制比 {:.2f}%'.format(rate * 100))
        reply_time = time.strftime("%Y-%m-%d", time.localtime(ctime))
        image = await create_image(content, username, reply_time)
        if not image:
            return None
        msg.append(MessageSegment.image(
            f"base64://{base64.b64encode(image).decode()}"))
        msg.append(f'链接：{reply_url}')
        return msg
    except:
        logger.debug(traceback.format_exc())
        return None


async def create_image(text, username, time):
    template = env.get_template('article.html')
    content = await template.render_async(text=text, username=username, time=time)
    async with get_new_page(viewport={"width": 500, "height": 100}) as page:
        await page.set_content(content)
        img = await page.screenshot(full_page=True)
    return img
