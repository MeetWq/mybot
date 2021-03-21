import os
import re
import shutil
import requests
import traceback
import subprocess
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from urllib.parse import quote
from nonebot.log import logger
from nonebot.adapters.cqhttp import Message, MessageSegment

import wikipedia
from wikipedia import WikipediaException
from baike import getBaike

dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

wikipedia.set_lang("zh")


async def get_content(keyword, source, force=False):
    msg = ''
    if source == 'jiki':
        msg = await get_jiki_content(keyword, force)
    elif source == 'baidu':
        msg = await get_baidu_content(keyword, force)
    elif source == 'wiki':
        msg = await get_wiki_content(keyword, force)
    return msg


async def get_jiki_content(keyword, force=False):
    keyword = quote(keyword)
    search_url = 'https://jikipedia.com/search?phrase={}'.format(keyword)
    try:
        search_resp = requests.get(search_url)
        if search_resp.status_code != 200:
            logger.warning('Search failed, url: ' + search_url)
            return ''

        if (not force and '对不起！小鸡词典暂未收录该词条' in search_resp.text) or \
                (force and '你可能喜欢的词条' not in search_resp.text):
            return ''

        search_result = BeautifulSoup(search_resp.content, 'lxml')
        masonry = search_result.find('div', {'class': 'masonry'})
        if not masonry:
            return ''

        card = masonry.find('div', recursive=False)
        card_content = card.find('a', {'class': 'card-content'})
        card_url = 'https://jikipedia.com' + card_content.get('href')

        card_resp = requests.get(card_url)
        if card_resp.status_code != 200:
            logger.warning('Get detail page failed, url: ' + card_url)
            return ''

        card_result = BeautifulSoup(card_resp.content, 'lxml')
        card_section = card_result.find('div', {'class': 'section card-middle'})
        title = card_section.find('div', {'class': 'title-container'}).find('span', {'class': 'title'}).text
        content = card_section.find('div', {'class': 'content'}).text
        images = card_section.find_all('div', {'class': 'show-images'})
        img_urls = []
        for image in images:
            img_urls.append(image.find('img').get('src'))

        msg = Message()
        msg.append(title + ':\n---------------\n')
        msg.append(content)
        for img_url in img_urls:
            img_path = await download_image(img_url)
            if img_path:
                msg.append(MessageSegment.image(file=img_path))
        return msg

    except (requests.exceptions.RequestException, AttributeError):
        logger.warning('Error in get content: ' + traceback.format_exc())
        return ''


async def get_baidu_content(keyword, force=False):
    try:
        content = getBaike(keyword, pic=True)
        if not content.strip():
            return ''
        match_obj = re.match(r'(.*?)(（.*?）)?\n(.*)', content)
        if not match_obj:
            return ''
        title = match_obj.group(1)
        subtitle = match_obj.group(2)
        text = match_obj.group(3)
        if not force:
            if fuzz.ratio(title, keyword) < 90:
                return ''

        msg = Message()
        msg.append(title)
        if subtitle:
            msg.append(subtitle)
        msg.append(':\n---------------\n' + text)
        img_ext = ['.jpg', '.png', '.gif']
        for ext in img_ext:
            file_name = title + '_1' + ext
            if os.path.exists(file_name):
                file_path = os.path.join(cache_path, file_name)
                shutil.move(file_name, file_path)
                msg.append(MessageSegment.image(file=file_path))
                break
        return msg
    except (requests.exceptions.RequestException, AttributeError):
        logger.warning('Error in get content: ' + traceback.format_exc())
        return ''


async def get_wiki_content(keyword, force=False):
    try:
        entries = wikipedia.search(keyword)
        if len(entries) < 1:
            return ''
        title = entries[0]
        if not force:
            if fuzz.ratio(title, keyword) < 90:
                return ''

        content = wikipedia.summary(title)
        return title + ':\n---------------\n' + content
    except WikipediaException:
        logger.warning('Error in get content: ' + traceback.format_exc())
        return ''


async def download_image(img_url: str):
    img_path = os.path.join(cache_path, os.path.basename(img_url))
    try:
        if not os.path.exists(img_path):
            download_cmd = 'wget -4 {} -O {}'.format(img_url, img_path)
            logger.debug(download_cmd)
            status = subprocess.check_call(
                download_cmd, shell=True, timeout=30)
            if status != 0:
                logger.warning('Image {} download failed!'.format(img_path))
                if os.path.exists(img_path):
                    os.remove(img_path)
                return ''
            logger.info('Image {} download successfully!'.format(img_path))
        return img_path
    except:
        logger.warning('Error downloading image! ' + traceback.format_exc())
        return ''
