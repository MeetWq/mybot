import os
import time
import traceback
import subprocess
from PIL import ImageFont
from pyppeteer import launch
from pyppeteer.chromium_downloader import check_chromium, download_chromium

from nonebot.log import logger

dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

if not check_chromium():
    download_chromium()


async def create_logo(left_text, right_text, style='pornhub'):
    img_path = ''
    if style == 'pornhub':
        img_path = await create_pornhub_logo(left_text, right_text)
    elif style == 'youtube':
        img_path = await create_youtube_logo(left_text, right_text)
    return img_path


async def create_pornhub_logo(left_text, right_text):
    font_path = os.path.join(dir_path, 'arial.ttf')
    html_path = os.path.join(dir_path, 'pornhub.html')
    raw_path = os.path.join(cache_path, 'raw.png')
    trim_path = os.path.join(cache_path, 'trim.png')

    try:
        font = ImageFont.truetype(font_path, 100)
        font_width, font_height = font.getsize(left_text + right_text)

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('Porn', left_text).replace('Hub', right_text)

        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.setViewport(viewport={'width': font_width * 2, 'height': 300})
        await page.setJavaScriptEnabled(enabled=True)
        await page.setContent(content)
        await page.screenshot({'path': raw_path})
        await browser.close()

        if trim_image(raw_path, trim_path):
            return trim_path
        return ''
    except:
        logger.debug(traceback.format_exc())
        return ''


async def create_youtube_logo(left_text, right_text):
    font_path = os.path.join(dir_path, 'arial.ttf')
    html_path = os.path.join(dir_path, 'youtube.html')
    raw_path = os.path.join(cache_path, 'raw.png')
    trim_path1 = os.path.join(cache_path, 'trim1.png')
    trim_path2 = os.path.join(cache_path, 'trim2.png')

    try:
        font = ImageFont.truetype(font_path, 100)
        font_width, font_height = font.getsize(left_text + right_text)

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('You', left_text).replace('Tube', right_text)

        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.setViewport(viewport={'width': font_width * 3, 'height': 300})
        await page.setJavaScriptEnabled(enabled=True)
        await page.setContent(content)
        time.sleep(2)
        await page.screenshot({'path': raw_path})
        await browser.close()

        if trim_image(raw_path, trim_path1):
            if trim_image(trim_path1, trim_path2):
                return trim_path2
        return ''
    except:
        logger.debug(traceback.format_exc())
        return ''


def trim_image(input_path, output_path):
    stdout = open(os.devnull, 'w')
    p_open = subprocess.Popen('convert {} -trim {}'.format(input_path, output_path),
                              shell=True, stdout=stdout, stderr=stdout)
    p_open.wait()
    stdout.close()

    if p_open.returncode != 0:
        return False
    return True
