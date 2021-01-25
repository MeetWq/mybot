from nonebot import get_driver

from .data_source import MyCC98Api
from .config import Config

global_config = get_driver().config
cc98_config = Config(**global_config.dict())

cc98_api = MyCC98Api(cc98_config.cc98_user_name, cc98_config.cc98_user_password)
