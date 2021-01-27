import os
import requests
import traceback
import subprocess
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
setu_config = Config(**global_config.dict())


async def get_pic_url(key_word=None) -> str:
    data = {
        'apikey': setu_config.setu_apikey,
        'r18': 0,
        'num': 1,
        'size1200': 1,
        'keyword': key_word
    }
    try:
        response = requests.get('https://api.lolicon.app/setu/', params=data, timeout=5).json()
        if response['code'] != 0:
            logger.warning('Error getting setu! ' + traceback.format_exc())
            return ''
        url = response['data'][0]['url']
        logger.info('Get setu url: ' + url)
        return url
    except requests.exceptions.RequestException:
        logger.warning('Error getting setu! ' + traceback.format_exc())
        return ''


async def download_image(img_url: str, img_path: str):
    try:
        if os.path.exists(img_path):
            return True
        download_cmd = 'wget -4 {} -O {}'.format(img_url, img_path)
        logger.debug(download_cmd)
        status = subprocess.check_call(download_cmd, shell=True, timeout=30)
        if status == 0:
            logger.info('Image {} download successfully!'.format(img_path))
            return True
        else:
            logger.warning('Image {} download failed!'.format(img_path))
            if os.path.exists(img_path):
                os.remove(img_path)
            return False
    except:
        logger.warning('Error downloading image! ' + traceback.format_exc())
        return False
