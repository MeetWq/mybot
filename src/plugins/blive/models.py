from typing import Optional

from nonebot_plugin_saa import PlatformTarget
from pydantic import BaseModel


class BiliUser(BaseModel):
    uid: int
    """ B站用户uid """
    name: str
    """ B站用户名 """
    room_id: Optional[int] = None
    """ B站直播间id """


class SubscriptionOptions(BaseModel):
    live: bool = True
    """ 是否推送直播 """
    dynamic: bool = True
    """ 是否推送动态 """
    record: bool = False
    """ 是否录播 """


class Subscription(BaseModel):
    target: PlatformTarget
    """ 发送目标 """
    user: BiliUser
    """ B站用户信息 """
    options: SubscriptionOptions
