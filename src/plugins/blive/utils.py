import datetime
import traceback
from typing import Optional

from bilireq.user import get_user_info
from bilireq.utils import get
from nonebot.log import logger
from nonebot_plugin_htmlrender import get_new_page

from .auth import AuthManager
from .models import BiliUser

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
)


async def get_user_info_by_uid(uid: int) -> Optional[BiliUser]:
    res = await get_user_info(uid, cookies=AuthManager.get_cookies())
    if res:
        return BiliUser(
            uid=int(res["mid"]),
            name=res["name"],
            room_id=int(res["live_room"]["roomid"]) if res["live_room"] else None,
        )


async def get_user_info_by_name(name: str) -> Optional[BiliUser]:
    url = "https://api.bilibili.com/x/web-interface/wbi/search/type"
    params = {"search_type": "bili_user", "keyword": name}
    resp = await get(url, params=params, cookies=AuthManager.get_cookies())
    for user in resp["result"]:
        if user["uname"] == name:
            return BiliUser(
                uid=int(user["mid"]),
                name=user["uname"],
                room_id=int(user["room_id"]) if user["room_id"] else None,
            )


async def get_user_dynamics(uid: int):
    url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space"
    data = {"host_mid": uid}
    headers = {
        "User-Agent": USER_AGENT,
        "Origin": "https://space.bilibili.com",
        "Referer": f"https://space.bilibili.com/{uid}/dynamic",
    }
    return await get(
        url, params=data, headers=headers, cookies=AuthManager.get_cookies()
    )


async def get_dynamic_screenshot(dynamic_id: int) -> Optional[bytes]:
    url = f"https://t.bilibili.com/{dynamic_id}"
    try:
        async with get_new_page(
            viewport={"width": 2000, "height": 1000},
            user_agent=USER_AGENT,
            device_scale_factor=3,
        ) as page:
            cookies = AuthManager.get_cookies()
            await page.context.add_cookies(
                [
                    {
                        "domain": ".bilibili.com",
                        "name": name,
                        "path": "/",
                        "value": value,
                    }
                    for name, value in cookies.items()
                ]
            )
            await page.goto(url, wait_until="networkidle")
            # 动态被删除或者进审核了
            if page.url == "https://www.bilibili.com/404":
                logger.warning(f"动态 {dynamic_id} 不存在")
                return
            await page.wait_for_load_state(state="domcontentloaded")
            card = await page.query_selector(".card")
            assert card
            clip = await card.bounding_box()
            assert clip
            bar = await page.query_selector(".bili-tabs__header")
            assert bar
            bar_bound = await bar.bounding_box()
            assert bar_bound
            clip["height"] = bar_bound["y"] - clip["y"]
            return await page.screenshot(clip=clip, full_page=True)
    except Exception:
        logger.warning(
            f"Error in get_dynamic_screenshot({url}): {traceback.format_exc()}"
        )


def calc_time_total(t: float):
    """
    Calculate the total time in a human-readable format.
    Args:
    t (float | int): The time in seconds.
    Returns:
    str: The total time in a human-readable format.
    Example:
    >>> calc_time_total(4.5)
    '4500 毫秒'
    >>> calc_time_total(3600)
    '1 小时'
    >>> calc_time_total(3660)
    '1 小时 1 分钟'
    """
    t = int(t * 1000)
    if t < 5000:
        return f"{t} 毫秒"
    timedelta = datetime.timedelta(seconds=t // 1000)
    day = timedelta.days
    hour, mint, sec = tuple(int(n) for n in str(timedelta).split(",")[-1].split(":"))
    total = ""
    if day:
        total += f"{day} 天 "
    if hour:
        total += f"{hour} 小时 "
    if mint:
        total += f"{mint} 分钟 "
    if sec and not day and not hour:
        total += f"{sec} 秒 "
    return total
