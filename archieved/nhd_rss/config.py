from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    nhd_rss_url: str = ""
    nhd_rss_interval: int = 300
    nhd_rss_targets: list[dict] = []


rss_config = get_plugin_config(Config)
