import traceback
from typing import Optional

import httpx
from bilireq.user import get_user_info
from bilireq.utils import DEFAULT_HEADERS, get
from nonebot.log import logger
from nonebot_plugin_htmlrender import get_new_page

from .config import blive_config
from .models import BiliUser

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
)


async def search_user(keyword: str):
    url = "https://api.bilibili.com/x/web-interface/search/type"
    data = {"keyword": keyword, "search_type": "bili_user"}
    headers = {"user-agent": USER_AGENT, "Cookie": blive_config.bilibili_cookie}
    async with httpx.AsyncClient(timeout=10) as client:
        await client.get("https://www.bilibili.com", headers=headers)
        resp = await client.get(url, params=data)
        return resp.json()["data"]


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


async def get_user_dynamics(uid: int):
    url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space"
    data = {"host_mid": uid}
    headers = {
        **DEFAULT_HEADERS,
        **{
            "Origin": "https://space.bilibili.com",
            "Referer": f"https://space.bilibili.com/{uid}/dynamic",
            "Cookie": blive_config.bilibili_cookie,
        },
    }
    return await get(url, params=data, headers=headers, timeout=20)


async def get_dynamic_screenshot(dynamic_id: int) -> Optional[bytes]:
    url = f"https://t.bilibili.com/{dynamic_id}"
    try:
        async with get_new_page(
            viewport={"width": 2000, "height": 1000},
            user_agent=USER_AGENT,
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
