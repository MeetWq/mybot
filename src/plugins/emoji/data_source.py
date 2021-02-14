import os
import re
import random
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


def get_emoji_path(name: str):
    patterns = [(r'ac\d{2,4}', 'ac'),
                (r'em\d{2}', 'em'),
                (r'[acf]:?\d{3}', 'mahjong'),
                (r'ms\d{2}', 'ms'),
                (r'tb\d{2}', 'tb'),
                (r'[Cc][Cc]98\d{2}', 'cc98')]

    name = name.strip().split('.')[0].replace(':', '').lower()
    file_ext = ['.jpg', '.png', '.gif']
    for pattern, dir_name in patterns:
        if re.match(pattern, name):
            file_full_name = os.path.join(dir_path, 'images', dir_name, name)
            for ext in file_ext:
                file_path = file_full_name + ext
                if os.path.exists(file_path):
                    return file_path
    return None


async def get_image(keyword):
    keyword = quote(keyword)
    search_url = 'https://fabiaoqing.com/search/bqb/keyword/{}/type/bq/page/1.html'.format(keyword)
    try:
        search_resp = requests.get(search_url)
        if search_resp.status_code != 200:
            logger.warning('Search failed, url: ' + search_url)
            return ''
        search_result = BeautifulSoup(search_resp.content, 'lxml')
        images = search_result.find_all('div', {'class': 'searchbqppdiv tagbqppdiv'})
        image_num = len(images)
        if image_num <= 0:
            logger.warning('Can not find corresponding image! : ' + keyword)
            return ''
        if image_num >= 5:
            images = images[:5]
        random.shuffle(images)
        return images[0].img['data-original']
    except requests.exceptions.RequestException:
        logger.warning('Error getting image! ' + traceback.format_exc())
        return ''


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
