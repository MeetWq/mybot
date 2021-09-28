import random
import aiohttp
import traceback
from pixivpy_async import PixivClient, AppPixivAPI
from nonebot import get_driver
from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
pixiv_config = Config(**global_config.dict())
proxy = global_config.socks_proxy


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


async def search_by_image(img_url):
    url = 'https://saucenao.com/search.php'
    params = {
        'url': img_url,
        'numres': 1,
        'testmode': 1,
        'db': 5,
        'output_type': 2,
        'api_key': pixiv_config.saucenao_apikey
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Referer": url,
        "Origin": "https://saucenao.com",
        "Host": "saucenao.com"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, headers=headers) as resp:
                result = await resp.json()

        if result['header']['status'] == -1:
            logger.warning(f"post saucenao failed：{result['header']['message']}")
            return None

        if result['header']['status'] == -2:
            return '24小时内搜索次数到达上限！'

        if 'results'not in result or not result['results']:
            return '找不到相似的图片'

        res = result['results'][0]
        header = res['header']
        data = res['data']
        thumb_url = header["thumbnail"]

        msg = f"搜索到如下结果：\n" \
            f"相似度：{header['similarity']}%\n" \
            f"题目：{data['title']}\n" \
            f"pixiv id：{data['pixiv_id']}\n" \
            f"作者：{data['member_name']}\n" \
            f"作者id：{data['member_id']}\n"
        ext_url = ', '.join(data['ext_urls'])
    except:
        logger.debug(traceback.format_exc())
        return None

    try:
        illust = await get_by_id(data['pixiv_id'])
        if illust:
            ext_url = illust['illust']['meta_single_page']['original_image_url'].replace('i.pximg.net', 'i.pixiv.cat')
    except:
        pass

    msg += f"链接：{ext_url}"
    msgs = Message()
    msgs.append(msg)
    msgs.append(MessageSegment.image(thumb_url))
    return msgs
