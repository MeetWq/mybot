import traceback
from mcstatus import MinecraftServer
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.log import logger


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
