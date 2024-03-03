from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    blive_live_interval: int = 10
    blive_dynamic_interval: int = 30
    blrec_address: str = "http://your_address"
    bilibili_cookie: str = ""


blive_config = get_plugin_config(Config)
