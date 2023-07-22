import traceback
from typing import Optional

from bilireq.user import get_user_info
from bilireq.utils import get
from nonebot.log import logger
from nonebot_plugin_htmlrender import get_new_page

from .models import BiliUser


async def search_user(keyword: str):
    url = "https://api.bilibili.com/x/web-interface/search/type"
    data = {"keyword": keyword, "search_type": "bili_user"}
    return await get(url, params=data)


async def get_uset_info_by_uid(uid: str) -> Optional[BiliUser]:
    res = await get_user_info(uid, reqtype="web")
    if res:
        return BiliUser(
            uid=res["mid"],
            name=res["name"],
            room_id=res["live_room"]["roomid"] if res["live_room"] else None,
        )


async def get_user_info_by_name(name: str) -> Optional[BiliUser]:
    res = await search_user(name)
    if res and res["numResults"]:
        for data in res["result"]:
            if data["uname"] == name:
                return BiliUser(
                    uid=data["mid"],
                    name=data["uname"],
                    room_id=data["room_id"] if data["room_id"] else None,
                )


async def get_dynamic_screenshot(dynamic_id: int) -> Optional[bytes]:
    url = f"https://t.bilibili.com/{dynamic_id}"
    try:
        async with get_new_page(
            viewport={"width": 2000, "height": 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
            device_scale_factor=3,
        ) as page:
            await page.goto(url, wait_until="networkidle")
            # 动态被删除或者进审核了
            if page.url == "https://www.bilibili.com/404":
                return
            await page.wait_for_load_state(state="domcontentloaded")
            card = await page.query_selector(".card")
            assert card
            clip = await card.bounding_box()
            assert clip
            bar = await page.query_selector(".bili-dyn-action__icon")
            assert bar
            bar_bound = await bar.bounding_box()
            assert bar_bound
            clip["height"] = bar_bound["y"] - clip["y"]
            return await page.screenshot(clip=clip, full_page=True)
    except:
        logger.warning(
            f"Error in get_dynamic_screenshot({url}): {traceback.format_exc()}"
        )
