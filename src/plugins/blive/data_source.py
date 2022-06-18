import httpx
from typing import Optional
from nonebot.log import logger
from nonebot_plugin_htmlrender import get_new_page


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
            resp = await client.post(url, json={"uids": uids})
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
            resp = await client.get(url, params=params)
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
            resp = await client.get(url)
            result = resp.json()
        return result["data"]["cards"]
    except Exception as e:
        logger.warning(f"Error in get_user_dynamics({uid}): {e}")
        return []


async def get_dynamic_screenshot(url: str) -> Optional[bytes]:
    try:
        async with get_new_page(
            viewport={"width": 360, "height": 780},
            user_agent="Mozilla/5.0 (Linux; Android 10; RMX1911) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36",
            device_scale_factor=2,
        ) as page:
            await page.goto(url, wait_until="networkidle", timeout=10000)
            content = await page.content()
            content = content.replace(
                '<div class="dyn-header__right">'
                '<div data-pos="follow" class="dyn-header__following">'
                '<span class="dyn-header__following__icon"></span>'
                '<span class="dyn-header__following__text">关注</span></div></div>',
                "",
            )  # 去掉关注按钮
            content = content.replace(
                '<div class="dyn-card">',
                '<div class="dyn-card" '
                'style="font-family: sans-serif; overflow-wrap: break-word;">',
            )
            # 1. 字体问题：.dyn-class里font-family是PingFangSC-Regular，使用行内CSS覆盖掉它
            # 2. 换行问题：遇到太长的内容（长单词、某些长链接等）允许强制换行，防止溢出
            content = content.replace(
                '<div class="launch-app-btn dynamic-float-openapp">'
                '<div class="m-dynamic-float-openapp">'
                "<span>打开APP，查看更多精彩内容</span></div> <!----></div>",
                "",
            )  # 去掉打开APP的按钮，防止遮挡较长的动态
            await page.set_content(content)
            card = await page.query_selector(".dyn-card")
            assert card
            clip = await card.bounding_box()
            assert clip
            img = await page.screenshot(clip=clip, full_page=True)
            return img
    except Exception as e:
        logger.warning(f"Error in get_dynamic_screenshot({url}): {e}")
        return None
