import os
import requests
import traceback
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import quote
from nonebot.log import logger

dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)


async def get_content(keyword):
    keyword = quote(keyword)
    search_url = 'https://jikipedia.com/search?phrase={}'.format(keyword)
    try:
        search_resp = requests.get(search_url)
        if search_resp.status_code != 200:
            logger.warning('Search failed, url: ' + search_url)
            return '', '', ''

        search_result = BeautifulSoup(search_resp.content, 'lxml')
        masonry = search_result.find('div', {'class': 'masonry'})

        if '对不起！小鸡词典暂未收录该词条' in search_resp.text or not masonry:
            print('找不到')
            return '', '', ''

        card = masonry.find('div', recursive=False)
        card_content = card.find('a', {'class': 'card-content'})
        card_url = 'https://jikipedia.com' + card_content.get('href')

        card_resp = requests.get(card_url)
        if card_resp.status_code != 200:
            logger.warning('Get detail page failed, url: ' + card_url)
            return '', '', ''

        card_result = BeautifulSoup(card_resp.content, 'lxml')
        card_section = card_result.find('div', {'class': 'section card-middle'})
        title = card_section.find('div', {'class': 'title-container'}).text
        content = card_section.find('div', {'class': 'content'}).text
        images = card_section.find_all('div', {'class': 'show-images'})
        image_urls = []
        for image in images:
            image_urls.append(image.find('img').get('src'))

        return title, content, image_urls

    except (requests.exceptions.RequestException, AttributeError):
        logger.warning('Error in get content: ' + traceback.format_exc())
        return '', '', ''


async def download_image(img_url: str):
    img_path = os.path.join(cache_path, os.path.basename(img_url))
    try:
        if not os.path.exists(img_path):
            download_cmd = 'wget -4 {} -O {}'.format(img_url, img_path)
            logger.debug(download_cmd)
            status = subprocess.check_call(download_cmd, shell=True, timeout=30)
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
