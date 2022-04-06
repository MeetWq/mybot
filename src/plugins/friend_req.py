import asyncio
from nonebot import on_request
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import FriendRequestEvent
from nonebot.log import logger


async def _friend_req(event: FriendRequestEvent) -> bool:
    logger.info(f"FriendRequestEvent: {event.user_id}")
    return True


friend_req = on_request(_friend_req, priority=5)


@friend_req.handle()
async def _(bot: Bot, event: FriendRequestEvent):
    # await asyncio.sleep(5)
    # await event.approve(bot)
    await bot.send_private_msg(
        user_id=int(list(bot.config.superusers)[0]),
        message=f"{event.user_id} 请求添加好友",
    )
