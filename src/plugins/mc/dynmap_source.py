import httpx
from nonebot.log import logger
from datetime import datetime, timedelta


async def get_dynmap_updates(url: str):
    try:
        stamp = (datetime.now() - timedelta(minutes=2)).timestamp()
        url += "/" + str(int(stamp * 1000))
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url)
            result = resp.json()
        return result
    except Exception as e:
        logger.warning(f"Error in get_dynmap_updates({url}): {e}")
        return None


async def get_status(url: str) -> str:
    result = await get_dynmap_updates(url)
    if not result:
        return ""
    players = result["players"]
    players = [p["account"] for p in players]
    players = ", ".join(players)
    tick = result["servertime"]
    tick = tick - 18000
    tick = tick + 24000 if tick < 0 else tick
    tick = tick * 36
    stime = "{:02d}:{:02d}:{:02d}.{:01d}".format(
        tick // 10 // 60 // 60, tick // 10 // 60 % 60, tick // 10 % 60, tick % 10
    )
    storm = result["hasStorm"]
    thunder = result["isThundering"]
    weather = "☀" if not storm else "⛈" if thunder else "🌧"
    status = f"当前在线：{players}\n服务器时间：{stime}\n服务器天气：{weather}"
    return status


async def send_message(config, msg):
    try:
        login_url = config["url"] + "/up/login"
        send_url = config["url"] + "/up/sendmessage"
        info = {"j_username": config["username"], "j_password": config["password"]}
        data = {"name": "", "message": msg}
        async with httpx.AsyncClient(timeout=20) as client:
            await client.post(login_url, data=info)
            await client.post(send_url, json=data)
        return True
    except Exception as e:
        logger.warning(f"Error in send_message({config}, {msg}): {e}")
        return False
