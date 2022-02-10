import json
import jinja2
import random
import traceback
from pathlib import Path
from datetime import datetime
from typing import Union, Optional

from nonebot import get_driver
from nonebot_plugin_htmlrender import html_to_pic
from nonebot.log import logger

from .config import Config

fortune_config = Config.parse_obj(get_driver().config.dict())

dir_path = Path(__file__).parent
resource_path = dir_path / "resources"
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)

data_path = Path("data/fortune")
if not data_path.exists():
    data_path.mkdir(parents=True)


async def get_fortune(user_id, username) -> Optional[Union[str, bytes]]:
    try:
        log_path = data_path / (datetime.now().strftime("%Y%m%d") + ".json")
        if log_path.exists():
            log = json.load(log_path.open("r", encoding="utf-8"))
        else:
            log = {}

        if user_id not in log:
            copywriting = get_copywriting()
            luck = copywriting["luck"]
            content = copywriting["content"]
            fortune = get_type(luck)
            face = get_face(luck)
            image = await create_image(username, luck, fortune, content, face)
            if image:
                log[user_id] = fortune
                json.dump(log, log_path.open("w", encoding="utf-8"), ensure_ascii=False)
                return image
        else:
            fortune = log[user_id]
            return "你今天已经抽过签了，你的今日运势是：" + fortune
    except:
        logger.warning(traceback.format_exc())
        return None


def get_copywriting() -> dict:
    path = resource_path / "copywriting.json"
    with path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return random.choice(data["copywriting"])


def get_type(luck) -> str:
    path = resource_path / "types.json"
    with open(path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    types = data["types"]
    for type in types:
        if luck == type["luck"]:
            return type["name"]
    return ""


def get_face(luck) -> str:
    if luck in [10]:
        face_id = "04"
    elif luck in [9, 20]:
        face_id = "05"
    elif luck in [8, 26]:
        face_id = "09"
    elif luck in [7, 27]:
        face_id = "07"
    elif luck in [6, 25]:
        face_id = "10"
    elif luck in [5]:
        face_id = "03"
    elif luck in [4]:
        face_id = "01"
    elif luck in [21, 22]:
        face_id = "02"
    elif luck in [23, 24]:
        face_id = "06"
    elif luck in [-6]:
        face_id = "08"
    elif luck in [-7]:
        face_id = "11"
    elif luck in [-8, -9, -10]:
        face_id = "12"
    else:
        face_id = "01"
    return f"cc98{face_id}.png"


async def create_image(username, luck, fortune, content, face) -> bytes:
    if len(username) > 50:
        username = username[:50] + "..."

    template = env.get_template("fortune.html")
    html = await template.render_async(
        username=username,
        luck=luck,
        fortune=fortune,
        content=content,
        face=face,
        style=fortune_config.fortune_style,
    )
    return await html_to_pic(
        html,
        viewport={"width": 100, "height": 100},
        template_path=f"file://{template_path.absolute()}",
    )
