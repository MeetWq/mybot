from typing import Annotated

from nonebot import require
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.params import Depends

require("nonebot_plugin_uninfo")

from nonebot_plugin_uninfo import Uninfo

from .config import blacklist_config


def get_user_id(uninfo: Uninfo) -> str:
    return f"{uninfo.scope}_{uninfo.self_id}_{uninfo.scene_path}"


UserId = Annotated[str, Depends(get_user_id)]


@run_preprocessor
async def _(user_id: UserId):
    if user_id in blacklist_config.blocked_userids:
        reason = f"User '{user_id}' is in the blacklist"
        logger.debug(reason)
        raise IgnoredException(reason)
