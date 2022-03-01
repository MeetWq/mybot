import httpx
import base64
import jinja2
import traceback
from pathlib import Path
from typing import List, Union, Optional
from nonebot import get_driver
from nonebot.log import logger
from nonebot_plugin_htmlrender import html_to_pic

from .config import Config

dd_config = Config.parse_obj(get_driver().config.dict())

dir_path = Path(__file__).parent
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)


async def get_uid_by_name(name: str) -> int:
    try:
        url = "http://api.bilibili.com/x/web-interface/search/type"
        params = {"search_type": "bili_user", "keyword": name}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            result = resp.json()
        if not result or result["code"] != 0:
            return -1
        users = result["data"]["result"]
        for user in users:
            if user["uname"] == name:
                return user["mid"]
        return -1
    except Exception as e:
        logger.warning(f"Error in get_uid_by_name({name}): {e}")
        return -1


async def get_user_info(uid: int) -> dict:
    try:
        url = "http://api.bilibili.com/x/web-interface/card"
        params = {"mid": uid}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            result = resp.json()
        if not result or result["code"] != 0:
            return {}
        return result["data"]["card"]
    except Exception as e:
        logger.warning(f"Error in get_user_info({uid}): {e}")
        return {}


async def get_same_followings(uid: int, cookie: str) -> List[dict]:
    try:
        all_users: List[dict] = []
        url = "http://api.bilibili.com/x/relation/same/followings"
        headers = {"cookie": cookie}
        async with httpx.AsyncClient() as client:
            for i in range(40):
                params = {"vmid": uid, "ps": 50, "pn": i + 1}
                resp = await client.get(url, params=params, headers=headers)
                result = resp.json()
                if not result or result["code"] != 0:
                    continue
                users = result["data"]["list"]
                if not users:
                    break
                all_users.extend(users)
        return all_users
    except Exception as e:
        logger.warning(f"Error in get_same_followings({uid}): {e}")
        return []


async def get_medals(uid: int, cookie: str) -> List[dict]:
    try:
        url = "https://api.live.bilibili.com/xlive/web-ucenter/user/MedalWall"
        params = {"target_id": uid}
        headers = {"cookie": cookie}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=headers)
            result = resp.json()
        if not result or result["code"] != 0:
            return []
        return result["data"]["list"]
    except Exception as e:
        logger.warning(f"Error in get_medals({uid}): {e}")
        return []


def format_color(color: int) -> str:
    return hex(color).replace("0x", "#")


async def get_reply(name: str) -> Optional[Union[str, bytes]]:
    try:
        if name.isdigit():
            uid = int(name)
        else:
            uid = await get_uid_by_name(name)
        info = await get_user_info(uid)
        if not info:
            return "获取用户信息失败，请检查名称或稍后再试"

        users1 = await get_same_followings(uid, cookie=dd_config.bili_user1_cookie)
        users2 = await get_same_followings(uid, cookie=dd_config.bili_user2_cookie)
        users = users1 + users2

        medals = await get_medals(uid, cookie=dd_config.bili_user1_cookie)
        medal_dict = {medal["target_name"]: medal for medal in medals}

        user_list = []
        for user in users:
            name = user["uname"]
            uid = user["mid"]
            medal = {}
            if name in medal_dict:
                medal_info = medal_dict[name]["medal_info"]
                medal = {
                    "name": medal_info["medal_name"],
                    "level": medal_info["level"],
                    "color_border": format_color(medal_info["medal_color_border"]),
                    "color_start": format_color(medal_info["medal_color_start"]),
                    "color_end": format_color(medal_info["medal_color_end"]),
                }
            user_list.append({"name": name, "uid": uid, "medal": medal})
        follows_num = int(info["attention"])
        vtbs_num = len(user_list)
        result = {
            "name": info["name"],
            "uid": info["mid"],
            "face": info["face"],
            "fans": info["fans"],
            "follows": info["attention"],
            "percent": f"{(vtbs_num/follows_num*100):.2f}% ({vtbs_num}/{follows_num})",
            "users": user_list,
        }
        template = env.get_template("info.html")
        content = await template.render_async(info=result)
        return await html_to_pic(
            content, wait=0, viewport={"width": 100, "height": 100}
        )
    except:
        logger.warning(traceback.format_exc())
        return None
