from typing import List

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    nhd_rss_url: str = ""
    nhd_rss_interval: int = 300
    nhd_rss_targets: List[dict] = []


rss_config = Config.parse_obj(get_driver().config.dict())
