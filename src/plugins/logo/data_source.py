import os
import uuid
import base64
import aiohttp
import asyncio
import traceback
import subprocess
from pathlib import Path
from PIL import ImageFont
from bs4 import BeautifulSoup
from pyppeteer import launch
from pyppeteer.chromium_downloader import check_chromium, download_chromium
from pyppeteer.errors import NetworkError

from nonebot.log import logger

dir_path = Path(__file__).parent
cache_path = Path('cache/logo')
if not cache_path.exists():
    cache_path.mkdir(parents=True)

if not check_chromium():
    download_chromium()


async def create_logo(texts, style='pornhub'):
    img_path = ''
    try:
        if style == 'pornhub':
            img_path = await create_pornhub_logo(texts[0], texts[1])
        elif style == 'youtube':
            img_path = await create_youtube_logo(texts[0], texts[1])
        elif style == 'douyin':
            img_path = await create_douyin_logo(' '.join(texts))
        elif style in ['cocacola', 'harrypotter']:
            img_path = await create_logomaker_logo(' '.join(texts), style)

        if img_path:
            return str(img_path.absolute())
        return ''
    except (AttributeError, TypeError, OSError, NetworkError):
        logger.debug(traceback.format_exc())
        return ''


async def create_pornhub_logo(left_text, right_text):
    font_path = Path('src/data/fonts/arial.ttf')
    html_path = dir_path / 'pornhub.html'
    img_path = cache_path / (uuid.uuid1().hex + '.png')

    font = ImageFont.truetype(str(font_path), 100)
    font_width, font_height = font.getsize(left_text + right_text)

    with html_path.open('r', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('Porn', left_text).replace('Hub', right_text)

    browser = await launch({'args': ['--no-sandbox']}, headless=True)
    page = await browser.newPage()
    await page.setViewport(viewport={'width': font_width * 2, 'height': 300})
    await page.setJavaScriptEnabled(enabled=True)
    await page.setContent(content)
    await page.screenshot({'path': str(img_path)})
    await browser.close()

    if trim_image(img_path, img_path):
        return img_path


async def create_youtube_logo(left_text, right_text):
    font_path = Path('src/data/fonts/arial.ttf')
    html_path = dir_path / 'youtube.html'
    img_path = cache_path / (uuid.uuid1().hex + '.png')

    font = ImageFont.truetype(str(font_path), 100)
    font_width, font_height = font.getsize(left_text + right_text)

    gfont1_path = dir_path / 'TK3iWkUHHAIjg752HT8Ghe4.woff2'
    gfont2_path = dir_path / 'TK3iWkUHHAIjg752Fj8Ghe4.woff2'
    gfont3_path = dir_path / 'TK3iWkUHHAIjg752Fz8Ghe4.woff2'
    gfont4_path = dir_path / 'TK3iWkUHHAIjg752GT8G.woff2'
    corner_path = dir_path / 'corner.png'

    with gfont1_path.open('rb') as f:
        gfont1_b64 = 'data:application/x-font-woff;charset=utf-8;base64,' + str(base64.b64encode(f.read()), 'utf-8')

    with gfont2_path.open('rb') as f:
        gfont2_b64 = 'data:application/x-font-woff;charset=utf-8;base64,' + str(base64.b64encode(f.read()), 'utf-8')

    with gfont3_path.open('rb') as f:
        gfont3_b64 = 'data:application/x-font-woff;charset=utf-8;base64,' + str(base64.b64encode(f.read()), 'utf-8')

    with gfont4_path.open('rb') as f:
        gfont4_b64 = 'data:application/x-font-woff;charset=utf-8;base64,' + str(base64.b64encode(f.read()), 'utf-8')

    with corner_path.open('rb') as f:
        corner_b64 = 'data:image/png;base64,' + str(base64.b64encode(f.read()), 'utf-8')

    with html_path.open('r', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('You', left_text).replace('Tube', right_text) \
                         .replace('FONT1', gfont1_b64).replace('FONT2', gfont2_b64) \
                         .replace('FONT3', gfont3_b64).replace('FONT4', gfont4_b64) \
                         .replace('CORNER', corner_b64)

    browser = await launch({'args': ['--no-sandbox']}, headless=True)
    page = await browser.newPage()
    await page.setViewport(viewport={'width': font_width * 3, 'height': 300})
    await page.setJavaScriptEnabled(enabled=True)
    await page.setContent(content)
    await page.screenshot({'path': str(img_path)})
    await browser.close()

    if trim_image(img_path, img_path):
        if trim_image(img_path, img_path):
            return img_path


async def create_douyin_logo(text):
    img_path = cache_path / (uuid.uuid1().hex + '.gif')

    browser = await launch({'args': ['--no-sandbox']}, headless=True)
    page = await browser.newPage()
    await page.goto('https://tools.miku.ac/douyin_text/')
    await page.evaluate('function() {document.querySelector("input[type=checkbox]").click()}')
    await asyncio.sleep(2)
    await page.evaluate('function() {document.querySelector("input[type=text]").value = ""}')
    await page.focus('input[type=text]')
    await page.keyboard.type(text)
    el_btn = await page.querySelector('button[class="el-button el-button--default"]')
    await el_btn.click()
    await asyncio.sleep(1)
    preview = await page.querySelector('div[class="nya-container preview pt"]')
    img = await preview.querySelector('img')
    url = await (await img.getProperty('src')).jsonValue()
    resp = await page.goto(url)
    content = await resp.buffer()
    with img_path.open('wb') as f:
        f.write(content)
    await browser.close()
    return img_path


async def create_logomaker_logo(text, style='cocacola'):
    img_path = cache_path / (uuid.uuid1().hex + '.png')

    url = 'https://logomaker.herokuapp.com/proc.php'
    params = {
        'type': '@' + style,
        'title': text,
        'scale': 200,
        'spaceheight': 0,
        'widthplus': 0,
        'heightplus': 0,
        'fontcolor': '#000000',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            result = await resp.text()
    result = BeautifulSoup(result, 'lxml')
    href = result.find('a', {'id': 'gdownlink'})
    if not href:
        return None

    link = 'https://logomaker.herokuapp.com/' + href['href']
    headers = {
        'Referer': 'https://logomaker.herokuapp.com/gstyle.php'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=headers) as resp:
            result = await resp.read()
    with img_path.open('wb') as f:
        f.write(result)
    return img_path


def trim_image(input_path, output_path):
    stdout = open(os.devnull, 'w')
    p_open = subprocess.Popen('convert {} -trim {}'.format(input_path, output_path),
                              shell=True, stdout=stdout, stderr=stdout)
    p_open.wait()
    stdout.close()

    if p_open.returncode != 0:
        return False
    return True
