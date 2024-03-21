from typing import List

from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    blocked_userids: List[str] = []


blacklist_config = get_plugin_config(Config)
