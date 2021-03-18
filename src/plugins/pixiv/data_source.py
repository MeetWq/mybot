import os
import random
import traceback
from pixivpy_async import *
from nonebot import get_driver
from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot.log import logger

import json
import base64
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ims.v20201229 import ims_client, models

from .config import Config

global_config = get_driver().config
pixiv_config = Config(**global_config.dict())
dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

r18_img = os.path.join(dir_path, 'r18.png')


async def get_pixiv(keyword: str, r18=False):
    try:
        if keyword.isdigit():
            illust = await get_by_id(int(keyword))
            if not illust:
                return '找不到该id的作品'
            illusts = [illust['illust']]
        elif keyword in ['日榜', 'day']:
            illusts = await get_by_ranking(mode='day')
        elif keyword in ['周榜', 'week']:
            illusts = await get_by_ranking(mode='week')
        elif keyword in ['月榜', 'month']:
            illusts = await get_by_ranking(mode='month')
        else:
            illusts = await get_by_search(keyword)
            if not illusts:
                return '找不到相关的作品'
        if not illusts:
            return '出错了，请稍后重试'
        logger.debug(illusts)
        msg = await to_msg(illusts, r18)
        return msg
    except (KeyError, TypeError):
        logger.debug(traceback.format_exc())
        return '出错了，请稍后重试'


async def to_msg(illusts, r18=False):
    msg = Message()
    async with PixivClient() as client:
        aapi = AppPixivAPI(client=client)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        for illust in illusts:
            msg.append('{} ({})'.format(illust['title'], illust['id']))
            url = illust['image_urls']['medium']
            file_name = os.path.basename(url)
            file_path = os.path.join(cache_path, file_name)
            if not os.path.exists(file_path):
                await aapi.download(url, path=cache_path, name=file_name)
            if not os.path.exists(file_path):
                return '下载出错，请稍后再试'
            if not r18:
                file_path = await replace_r18(file_path)
            msg.append(MessageSegment.image(file=file_path))
        return msg


async def get_by_ranking(mode='day', num=3):
    async with PixivClient() as client:
        aapi = AppPixivAPI(client=client)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illusts = await aapi.illust_ranking(mode)
        illusts = illusts['illusts']
        random.shuffle(illusts)
        return illusts[0:num]


async def get_by_search(keyword, num=3):
    async with PixivClient() as client:
        aapi = AppPixivAPI(client=client)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illusts = await aapi.search_illust(keyword)
        illusts = illusts['illusts']
        random.shuffle(illusts)
        return illusts[0:min(num, len(illusts))]


async def get_by_id(work_id):
    async with PixivClient() as client:
        aapi = AppPixivAPI(client=client)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illust = await aapi.illust_detail(work_id)
        return illust


async def replace_r18(path):
    try:
        cred = credential.Credential(pixiv_config.tencent_secret_id, pixiv_config.tencent_secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = 'ims.tencentcloudapi.com'

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = ims_client.ImsClient(cred, 'ap-shanghai', clientProfile)

        with open(path, 'rb') as f:
            img_b64 = str(base64.b64encode(f.read()), 'utf-8')

        req = models.ImageModerationRequest()
        params = {
            'FileContent': img_b64
        }
        req.from_json_string(json.dumps(params))

        resp = client.ImageModeration(req)
        resp = json.loads(resp.to_json_string())
        results = resp['LabelResults']
        for result in results:
            if result['Scene'] == 'Porn':
                if result['Suggestion'] == 'Pass':
                    return path
        return r18_img

    except TencentCloudSDKException as err:
        logger.debug(err)
        return r18_img
