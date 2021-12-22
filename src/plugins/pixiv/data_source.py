import httpx
import base64
import random
from pixivpy_async import PixivClient, AppPixivAPI
from nonebot import get_driver
from nonebot.adapters.cqhttp import MessageSegment, Message
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
pixiv_config = Config(**global_config.dict())
proxy = global_config.http_proxy
httpx_proxy = {
    'http://': global_config.http_proxy,
    'https://': global_config.http_proxy
}


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
        msg = await to_msg(illusts)
        return msg
    except Exception as e:
        logger.warning(f"Error in get_pixiv({keyword}): {e}")
        return '出错了，请稍后再试'


async def to_msg(illusts):
    msg = Message()
    async with PixivClient(proxy=proxy, timeout=20) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        for illust in illusts:
            try:
                url = illust['image_urls']['large']
                url = url.replace('_webp', '').replace(
                    'i.pximg.net', 'i.pixiv.re')
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=20)
                    result = resp.content
                if result:
                    msg.append('{} ({})'.format(illust['title'], illust['id']))
                    msg.append(MessageSegment.image(
                        f"base64://{base64.b64encode(result).decode()}"))
            except Exception as e:
                logger.warning(f"Error downloading {url}: {e}")
        return msg


async def get_by_ranking(mode='day', num=3):
    async with PixivClient(proxy=proxy, timeout=20) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illusts = await aapi.illust_ranking(mode)
        illusts = illusts['illusts']
        random.shuffle(illusts)
        return illusts[0:num]


async def get_by_search(keyword, num=3):
    async with PixivClient(proxy=proxy, timeout=20) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illusts = await aapi.search_illust(keyword)
        illusts = illusts['illusts']
        illusts = sorted(
            illusts, key=lambda i: i['total_bookmarks'], reverse=True)
        if len(illusts) > num * 3:
            illusts = illusts[0:int(len(illusts)/2)]
        random.shuffle(illusts)
        return illusts[0:min(num, len(illusts))]


async def get_by_id(work_id):
    async with PixivClient(proxy=proxy, timeout=20) as client:
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
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, params=params, headers=headers, timeout=20)
            result = resp.json()

        if result['header']['status'] == -1:
            logger.warning(
                f"post saucenao failed：{result['header']['message']}")
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
            f"作者id：{data['member_id']}\n" \
            f"链接：{', '.join(data['ext_urls'])}"
    except Exception as e:
        logger.warning(f"Error in search_by_image({url}): {e}")
        return None

    msgs = Message()
    msgs.append(msg)
    msgs.append(MessageSegment.image(thumb_url))
    return msgs
