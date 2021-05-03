import uuid
import aiohttp
import asyncio
import hashlib
import traceback
from pathlib import Path
from pyppeteer import launch
from pyppeteer.errors import NetworkError

from nonebot.log import logger

cache_path = Path('cache/petpet')
if not cache_path.exists():
    cache_path.mkdir(parents=True)

file_name = uuid.uuid1().hex
avatar_path = cache_path / (file_name + '.jpg')
petpet_path = cache_path / (file_name + '.gif')


async def get_petpet(user_id):
    avatar_url = 'http://q1.qlogo.cn/g?b=qq&nk={}&s=640'.format(user_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            result = await resp.read()
    md5 = hashlib.md5(result).hexdigest()
    if md5 == 'acef72340ac0e914090bd35799f5594e':
        avatar_url_small = 'http://q1.qlogo.cn/g?b=qq&nk={}&s=100'.format(user_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url_small) as resp:
                result = await resp.read()

    with avatar_path.open('wb') as f:
        f.write(result)

    status = await create_petpet(avatar_path, petpet_path)
    if status:
        return str(petpet_path.absolute())
    return ''


async def create_petpet(input_path, output_path):
    try:
        browser = await launch({'executablePath': '/usr/bin/chromium-browser', 'args': ['--no-sandbox']}, headless=True)
        page = await browser.newPage()
        await page.goto('https://benisland.neocities.org/petpet/')
        upload_file = await page.querySelector('input[type=file]')
        await upload_file.uploadFile(input_path)
        export_btn = await page.querySelector('button[id=export]')
        await export_btn.click()
        await asyncio.sleep(2)
        preview = await page.querySelector('figure[class=preview-image-container]')
        img = await preview.querySelector('img')
        url = await (await img.getProperty('src')).jsonValue()
        resp = await page.goto(url)
        content = await resp.buffer()
        with output_path.open('wb') as f:
            f.write(content)
        await browser.close()
        return True
    except (AttributeError, TypeError, OSError, NetworkError):
        logger.debug(traceback.format_exc())
        return False
