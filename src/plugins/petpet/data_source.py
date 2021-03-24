import os
import asyncio
import hashlib
import requests
import traceback
from pyppeteer import launch
from pyppeteer.chromium_downloader import check_chromium, download_chromium
from pyppeteer.errors import NetworkError

from nonebot.log import logger

dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

avatar_path = os.path.join(cache_path, 'avatar.jpg')
petpet_path = os.path.join(cache_path, 'petpet.gif')

if not check_chromium():
    download_chromium()


async def get_petpet(user_id):
    avatar_url = 'http://q1.qlogo.cn/g?b=qq&nk={}&s=640'.format(user_id)
    resp = requests.get(avatar_url)
    if resp.status_code != 200:
        return ''

    md5 = hashlib.md5(resp.content).hexdigest()
    if md5 == 'acef72340ac0e914090bd35799f5594e':
        avatar_url_small = 'http://q1.qlogo.cn/g?b=qq&nk={}&s=100'.format(user_id)
        resp = requests.get(avatar_url_small)
        if resp.status_code != 200:
            return ''

    with open(avatar_path, 'wb') as f:
        f.write(resp.content)
        
    print(file_md5)
    status = await create_petpet(avatar_path, petpet_path)
    if status:
        return petpet_path
    return ''


async def create_petpet(input_path, output_path):
    try:
        browser = await launch({'args': ['--no-sandbox']}, headless=True)
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
        with open(output_path, 'wb') as f:
            f.write(content)
        await browser.close()
        return True
    except (AttributeError, TypeError, OSError, NetworkError):
        logger.debug(traceback.format_exc())
        return False
