from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    wolframalpha_appid: str = ""


wolframalpha_config = get_plugin_config(Config)
