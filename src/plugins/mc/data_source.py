import io
import json
import base64
import jinja2
import aiohttp
import asyncio
import imageio
import traceback
from PIL import Image
from pathlib import Path
from mcstatus import MinecraftServer
from src.libs.playwright import get_new_page
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.log import logger

dir_path = Path(__file__).parent
template_path = dir_path / 'template'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                         enable_async=True)


async def get_mc_uuid(username: str) -> str:
    url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.read()
        if not result:
            return 'none'
        result = json.loads(result)
        return result['id']
    except:
        return ''


async def get_crafatar(type: str, uuid: str) -> Message:
    result = await _get_crafatar(type, uuid)
    if result:
        return MessageSegment.image(f'base64://{base64.b64encode(result).decode()}')
    return None


async def _get_crafatar(type: str, uuid: str) -> bytes:
    path = ''
    if type == 'avatar':
        path = 'avatars'
    elif type == 'head':
        path = 'renders/head'
    elif type == 'body':
        path = 'renders/body'
    elif type == 'skin':
        path = 'skins'
    elif type == 'cape':
        path = 'capes'

    url = f'https://crafatar.com/{path}/{uuid}?overlay'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.read()
        return result
    except:
        return None


def load_file(name):
    with (template_path / name).open('r', encoding='utf-8') as f:
        return f.read()


env.filters['load_file'] = load_file


async def get_mcmodel(uuid: str) -> Message:
    skin_bytes = await _get_crafatar('skin', uuid)
    cape_bytes = await _get_crafatar('cape', uuid)
    if not skin_bytes:
        return None
    skin = f'data:image/png;base64,{base64.b64encode(skin_bytes).decode()}'
    cape = f'data:image/png;base64,{base64.b64encode(cape_bytes).decode()}' if cape_bytes else ''

    try:
        template = env.get_template('skin.html')
        html = await template.render_async(skin=skin, cape=cape)

        images = []
        async with get_new_page(viewport={"width": 200, "height": 400}) as page:
            await page.set_content(html)
            await asyncio.sleep(0.1)
            for i in range(60):
                image = await page.screenshot(full_page=True)
                images.append(Image.open(io.BytesIO(image)))

        output = io.BytesIO()
        imageio.mimsave(output, images, format='gif', duration=0.01)
        return MessageSegment.image(f'base64://{base64.b64encode(output.getvalue()).decode()}')
    except:
        logger.warning(traceback.format_exc())
        return None


async def get_mcstatus(addr: str) -> str:
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
        msg.append(MessageSegment.image('base64://' + favicon.replace('data:image/png;base64,', '')))
    msg.append(
        f"服务端版本：{version}\n"
        f"协议版本：{protocol}\n"
        f"当前人数：{players_online}/{players_max}\n"
        f"在线玩家：{'、'.join(player_names)}\n"
        f"描述文本：{description}\n"
        f"游戏延迟：{latency}ms"
    )
    return msg
