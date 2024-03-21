from typing import Annotated

from nonebot import require
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import run_preprocessor

require("nonebot_plugin_session")

from nonebot_plugin_session import SessionId, SessionIdType

from .config import blacklist_config

UserId = Annotated[str, SessionId(SessionIdType.GROUP, include_bot_type=False)]


@run_preprocessor
async def _(user_id: UserId):
    if user_id in blacklist_config.blocked_userids:
        reason = f"User '{user_id}' is in the blacklist"
        logger.debug(reason)
        raise IgnoredException(reason)
