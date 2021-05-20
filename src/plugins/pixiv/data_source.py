import random
import traceback
from pixivpy_async import PixivClient, AppPixivAPI
from nonebot import get_driver
from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
pixiv_config = Config(**global_config.dict())
proxy = global_config.http_proxy


async def get_pixiv(keyword: str):
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
            return '出错了，请稍后再试'
        logger.debug(illusts)
        msg = await to_msg(illusts)
        return msg
    except (KeyError, TypeError):
        logger.debug(traceback.format_exc())
        return '出错了，请稍后再试'


async def to_msg(illusts):
    msg = Message()
    async with PixivClient(proxy=proxy) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        for illust in illusts:
            msg.append('{} ({})'.format(illust['title'], illust['id']))
            url = illust['image_urls']['large']
            url = url.replace('_webp', '').replace('i.pximg.net', 'i.pixiv.cat')
            msg.append(MessageSegment.image(file=url))
        return msg


async def get_by_ranking(mode='day', num=3):
    async with PixivClient(proxy=proxy) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illusts = await aapi.illust_ranking(mode)
        illusts = illusts['illusts']
        random.shuffle(illusts)
        return illusts[0:num]


async def get_by_search(keyword, num=3):
    async with PixivClient(proxy=proxy) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illusts = await aapi.search_illust(keyword)
        illusts = illusts['illusts']
        random.shuffle(illusts)
        return illusts[0:min(num, len(illusts))]


async def get_by_id(work_id):
    async with PixivClient(proxy=proxy) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illust = await aapi.illust_detail(work_id)
        return illust
