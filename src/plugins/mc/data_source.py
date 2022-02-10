from typing import Optional
import httpx
import base64
import jinja2
import asyncio
import imageio
import traceback
from PIL import Image
from io import BytesIO
from pathlib import Path
from mcstatus import MinecraftServer
from nonebot_plugin_htmlrender import get_new_page
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger

dir_path = Path(__file__).parent
template_path = dir_path / "template"
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path), enable_async=True
)


async def get_mc_uuid(username: str) -> str:
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            result = resp.json()
        if not result:
            return "none"
        return result.get("id", "none")
    except:
        return ""


async def get_crafatar(type: str, uuid: str) -> Optional[bytes]:
    path = ""
    if type == "avatar":
        path = "avatars"
    elif type == "head":
        path = "renders/head"
    elif type == "body":
        path = "renders/body"
    elif type == "skin":
        path = "skins"
    elif type == "cape":
        path = "capes"

    url = f"https://crafatar.com/{path}/{uuid}?overlay"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            result = resp.content
        return result
    except:
        return None


def load_file(name):
    with (template_path / name).open("r", encoding="utf-8") as f:
        return f.read()


env.filters["load_file"] = load_file


async def get_mcmodel(uuid: str) -> Optional[BytesIO]:
    skin_bytes = await get_crafatar("skin", uuid)
    cape_bytes = await get_crafatar("cape", uuid)
    if not skin_bytes:
        return None
    skin = f"data:image/png;base64,{base64.b64encode(skin_bytes).decode()}"
    cape = (
        f"data:image/png;base64,{base64.b64encode(cape_bytes).decode()}"
        if cape_bytes
        else ""
    )

    try:
        template = env.get_template("skin.html")
        html = await template.render_async(skin=skin, cape=cape)

        images = []
        async with get_new_page(viewport={"width": 200, "height": 400}) as page:
            await page.set_content(html)
            await asyncio.sleep(0.1)
            for i in range(60):
                image = await page.screenshot(full_page=True)
                images.append(Image.open(BytesIO(image)))

        output = BytesIO()
        imageio.mimsave(output, images, format="gif", duration=0.05)
        return output
    except:
        logger.warning(traceback.format_exc())
        return None


async def get_mcstatus(addr: str) -> Optional[Message]:
    try:
        server = MinecraftServer.lookup(addr)
        status = await server.async_status()
        version = status.version.name
        protocol = status.version.protocol
        players_online = status.players.online
        players_max = status.players.max
        players = status.players.sample
        player_names = [player.name for player in players] if players else []
        description = status.description
        latency = status.latency
        favicon = status.favicon
    except:
        logger.warning(traceback.format_exc())
        return None

    msg = Message()
    if favicon:
        msg.append(
            MessageSegment.image(
                "base64://" + favicon.replace("data:image/png;base64,", "")
            )
        )
    msg.append(
        f"服务端版本：{version}\n"
        f"协议版本：{protocol}\n"
        f"当前人数：{players_online}/{players_max}\n"
        f"在线玩家：{'、'.join(player_names)}\n"
        f"描述文本：{description}\n"
        f"游戏延迟：{latency}ms"
    )
    return msg
