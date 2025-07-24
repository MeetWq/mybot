from nonebot.plugin import get_plugin_config
from nonebot_plugin_saa import PlatformTarget
from pydantic import BaseModel


class Config(BaseModel):
    mczju_dynmap_url: str = ""
    mczju_dynmap_update_interval: int = 2
    mczju_dynmap_send_interval: int = 180
    mczju_dynmap_send_targets: list[dict] = []


mczju_config = get_plugin_config(Config)

dynmap_targets = [
    PlatformTarget.deserialize(target)
    for target in mczju_config.mczju_dynmap_send_targets
]
