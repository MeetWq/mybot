import json
import jinja2
import random
from pathlib import Path
from datetime import datetime

from nonebot import get_driver
from nonebot_plugin_htmlrender import html_to_pic

from .config import Config

fortune_config = Config.parse_obj(get_driver().config.dict())

dir_path = Path(__file__).parent
resource_path = dir_path / "resources"
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)

copywritings = []
with (resource_path / "copywriting.json").open("r", encoding="utf-8") as f:
    data = json.load(f)
for rank in data["copywriting"]:
    for content in rank["content"]:
        copywritings.append(
            {"fortune": rank["fortune"], "rank": rank["rank"], "content": content}
        )


async def get_fortune(user_id: int, username: str) -> bytes:
    date = datetime.now().strftime("%Y%m%d")
    random.seed(f"{date}-{user_id}")
    copywriting = random.choice(copywritings)
    fortune = copywriting["fortune"]
    rank = copywriting["rank"]
    content = copywriting["content"]
    face = get_face(rank)
    return await create_image(username, rank, fortune, content, face)


def get_face(rank: int) -> str:
    if rank in [10]:
        face_id = "04"
    elif rank in [9, 20]:
        face_id = "05"
    elif rank in [8, 26]:
        face_id = "09"
    elif rank in [7, 27]:
        face_id = "07"
    elif rank in [6, 25]:
        face_id = "10"
    elif rank in [5]:
        face_id = "03"
    elif rank in [4]:
        face_id = "01"
    elif rank in [21, 22]:
        face_id = "02"
    elif rank in [23, 24]:
        face_id = "06"
    elif rank in [-6]:
        face_id = "08"
    elif rank in [-7]:
        face_id = "11"
    elif rank in [-8, -9, -10]:
        face_id = "12"
    else:
        face_id = "01"
    return f"cc98{face_id}.png"


async def create_image(
    username: str, rank: int, fortune: str, content: str, face: str
) -> bytes:
    if len(username) > 50:
        username = username[:50] + "..."

    template = env.get_template("fortune.html")
    html = await template.render_async(
        username=username,
        type="good" if rank > 0 else "bad",
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
