from pathlib import Path
from typing import Optional

import httpx
from nonebot import get_driver
from nonebot.log import logger
from nonebot_plugin_htmlrender import get_new_page

from .config import Config

blive_config = Config.parse_obj(get_driver().config.dict())
headers = {
    "cookie": blive_config.bilibili_cookie,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
}


async def get_live_info(uid: str = "", up_name: str = "") -> dict:
    info = {}
    if uid:
        info = await get_live_info_by_uid(uid)
    elif up_name:
        info = await get_live_info_by_name(up_name)
    return info


async def get_live_info_by_uid(uid: str) -> dict:
    result = await get_live_info_by_uids([uid])
    if uid in result:
        return result[uid]
    return {}


async def get_live_info_by_uids(uids: list) -> dict:
    try:
        url = "https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json={"uids": uids}, headers=headers)
            result = resp.json()
        if not result or result["code"] != 0:
            return {}
        return result["data"]
    except Exception as e:
        logger.warning(f"Error in get_live_info_by_uids(): {e}")
        return {}


async def get_live_info_by_name(up_name: str) -> dict:
    user_info = await get_user_info_by_name(up_name)
    if not user_info:
        return {}
    return await get_live_info_by_uid(str(user_info["mid"]))


async def get_user_info_by_name(up_name: str) -> dict:
    try:
        url = "http://api.bilibili.com/x/web-interface/search/type"
        params = {"search_type": "bili_user", "keyword": up_name}
        async with httpx.AsyncClient() as client:
            await client.get("https://www.bilibili.com", headers=headers)
            resp = await client.get(url, params=params)
            result = resp.json()
        if not result or result["code"] != 0:
            return {}
        users = result["data"]["result"]
        for user in users:
            if user["uname"] == up_name:
                return user
        return {}
    except Exception as e:
        logger.warning(f"Error in get_user_info_by_name({up_name}): {e}")
        return {}


async def get_play_url(room_id: str) -> str:
    try:
        url = "http://api.live.bilibili.com/room/v1/Room/playUrl"
        params = {"cid": int(room_id), "platform": "web", "qn": 10000}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=headers)
            result = resp.json()
        if not result or result["code"] != 0:
            return ""
        return result["data"]["durl"][0]["url"]
    except Exception as e:
        logger.warning(f"Error in get_play_url({room_id}): {e}")
        return ""


async def get_user_dynamics(uid: str) -> list:
    try:
        # need_top: {1: 带置顶, 0: 不带置顶}
        url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id=0&need_top=0"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            result = resp.json()
        return result["data"]["cards"]
    except Exception as e:
        logger.warning(f"Error in get_user_dynamics({uid}): {e}")
        return []


async def get_dynamic_screenshot(dynamic_id: str) -> Optional[bytes]:
    url = f"https://m.bilibili.com/dynamic/{dynamic_id}"
    try:
        async with get_new_page(
            viewport={"width": 360, "height": 780},
            user_agent="Mozilla/5.0 (Linux; Android 10; RMX1911) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36",
            device_scale_factor=2,
        ) as page:
            await page.goto(url, wait_until="networkidle", timeout=10000)
            # 动态被删除或者进审核了
            if page.url == "https://m.bilibili.com/404":
                return None
            await page.add_script_tag(
                content=
                # 去除打开app按钮
                "document.getElementsByClassName('m-dynamic-float-openapp').forEach(v=>v.remove());"
                # 去除关注按钮
                "document.getElementsByClassName('dyn-header__following').forEach(v=>v.remove());"
                # 修复字体与换行问题
                "const dyn=document.getElementsByClassName('dyn-card')[0];"
                "dyn.style.fontFamily='Noto Sans CJK SC, sans-serif';"
                "dyn.style.overflowWrap='break-word'"
            )
            card = await page.query_selector(".dyn-card")
            assert card
            clip = await card.bounding_box()
            assert clip
            img = await page.screenshot(clip=clip, full_page=True)
            return img
    except Exception as e:
        logger.warning(f"Error in get_dynamic_screenshot({url}): {e}")
        return None
