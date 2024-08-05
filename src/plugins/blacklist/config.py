from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    blocked_userids: list[str] = []


blacklist_config = get_plugin_config(Config)
