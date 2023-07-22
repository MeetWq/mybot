from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    blive_live_interval: int = 10
    blive_dynamic_interval: int = 10
    blrec_address: str = "http://your_address"


blive_config = Config.parse_obj(get_driver().config.dict())
