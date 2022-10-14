from pydantic import BaseModel, Extra

from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    aidraw_api: str = ""
    aidraw_cd: int = 10


aidraw_config = Config.parse_obj(get_driver().config.dict())
