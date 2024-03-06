from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    fortune_style: str = "summer"


fortune_config = get_plugin_config(Config)
