import httpx
import random
from typing import Union
from pixivpy_async import PixivClient, AppPixivAPI

from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .config import Config

global_config = get_driver().config
pixiv_config = Config.parse_obj(global_config.dict())
proxy = str(global_config.http_proxy)


async def get_pixiv(keyword: str) -> Union[str, Message]:
    try:
        if keyword.isdigit():
            illust = await get_by_id(int(keyword))
            if not illust:
                return "找不到该id的作品"
            illusts = [illust["illust"]]
        elif keyword == "日榜":
            illusts = await get_by_ranking(mode="day")
        elif keyword == "周榜":
            illusts = await get_by_ranking(mode="week")
        elif keyword == "月榜":
            illusts = await get_by_ranking(mode="month")
        else:
            illusts = await get_by_search(keyword)
            if not illusts:
                return "找不到相关的作品"
        if not illusts:
            return "出错了，请稍后再试"
        msg = await to_msg(illusts)
        return msg
    except Exception as e:
        logger.warning(f"Error in get_pixiv({keyword}): {e}")
        return "出错了，请稍后再试"


async def to_msg(illusts) -> Message:
    msg = Message()
    async with PixivClient(proxy=proxy, timeout=20) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        for illust in illusts:
            try:
                url: str = illust["image_urls"]["large"]
                url = url.replace("_webp", "").replace("i.pximg.net", "i.pixiv.re")
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=20)
                    result = resp.content
                if result:
                    msg.append("{} ({})".format(illust["title"], illust["id"]))
                    msg.append(MessageSegment.image(result))
            except Exception as e:
                logger.warning(f"Error downloading image: {e}")
        return msg


async def get_by_ranking(mode="day", num=3):
    async with PixivClient(proxy=proxy, timeout=20) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illusts = await aapi.illust_ranking(mode)
        illusts = illusts["illusts"]
        random.shuffle(illusts)
        return illusts[0:num]


async def get_by_search(keyword, num=3):
    async with PixivClient(proxy=proxy, timeout=20) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illusts = await aapi.search_illust(keyword)
        illusts = illusts["illusts"]
        illusts = sorted(illusts, key=lambda i: i["total_bookmarks"], reverse=True)
        if len(illusts) > num * 3:
            illusts = illusts[0 : int(len(illusts) / 2)]
        random.shuffle(illusts)
        return illusts[0 : min(num, len(illusts))]


async def get_by_id(work_id):
    async with PixivClient(proxy=proxy, timeout=20) as client:
        aapi = AppPixivAPI(client=client, proxy=proxy)
        await aapi.login(refresh_token=pixiv_config.pixiv_token)
        illust = await aapi.illust_detail(work_id)
        return illust
