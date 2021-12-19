import json
import httpx
from nonebot.log import logger
from src.libs.playwright import get_new_page


async def get_live_info(uid: str = '', up_name: str = '') -> dict:
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
        url = 'https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids'
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=json.dumps({'uids': uids}))
            result = resp.json()
        if not result or result['code'] != 0:
            return {}
        return result['data']
    except Exception as e:
        logger.warning(f'Error in get_live_info_by_uids(): {e}')
        return {}


async def get_live_info_by_name(up_name: str) -> dict:
    user_info = await get_user_info_by_name(up_name)
    if not user_info:
        return {}
    return await get_live_info_by_uid(str(user_info['mid']))


async def get_user_info_by_name(up_name: str) -> dict:
    try:
        url = 'http://api.bilibili.com/x/web-interface/search/type'
        params = {
            'search_type': 'bili_user',
            'keyword': up_name
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            result = resp.json()
        if not result or result['code'] != 0:
            return {}
        users = result['data']['result']
        for user in users:
            if user['uname'] == up_name:
                return user
        return {}
    except Exception as e:
        logger.warning(f'Error in get_user_info_by_name({up_name}): {e}')
        return {}


async def get_play_url(room_id: int) -> str:
    try:
        url = 'http://api.live.bilibili.com/room/v1/Room/playUrl'
        params = {
            'cid': room_id,
            'platform': 'web',
            'qn': 10000
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            result = resp.json()
        if not result or result['code'] != 0:
            return ''
        return result['data']['durl'][0]['url']
    except Exception as e:
        logger.warning(f'Error in get_play_url({room_id}): {e}')
        return ''


async def get_user_dynamics(uid: str) -> dict:
    try:
        # need_top: {1: 带置顶, 0: 不带置顶}
        url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}&offset_dynamic_id=0&need_top=0'
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            result = resp.json()
        return result['data']['cards']
    except Exception as e:
        logger.warning(f'Error in get_user_dynamics({uid}): {e}')
        return []


async def get_dynamic_screenshot(url: str) -> bytes:
    try:
        async with get_new_page(viewport={"width": 392, "height": 30},
                                user_agent="Mozilla/5.0 (Linux; Android 11; Redmi K20 Pro Premium Edition) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/96.0.4664.55 Mobile Safari/537.36 EdgA/96.0.1054.41",
                                device_scale_factor=2.75) as page:
            await page.goto(url, wait_until='networkidle', timeout=10000)
            content = await page.content()
            content = content.replace('<div class="dyn-header__right">'
                                      '<div data-pos="follow" class="dyn-header__following">'
                                      '<span class="dyn-header__following__icon"></span>'
                                      '<span class="dyn-header__following__text">关注</span></div></div>', '')
            await page.set_content(content)
            card = await page.query_selector(".dyn-card")
            clip = await card.bounding_box()
            img = await page.screenshot(clip=clip, full_page=True)
            return img
    except Exception as e:
        logger.warning(f'Error in get_dynamic_screenshot({url}): {e}')
        return None
