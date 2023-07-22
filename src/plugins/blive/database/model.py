from typing import List, Optional

from nonebot_plugin_datastore import get_plugin_data
from nonebot_plugin_saa import PlatformTarget
from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import BiliUser, Subscription, SubscriptionOptions

Model = get_plugin_data().Model


class BiliUserRecord(Model):
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(64))
    """ B站用户uid """
    name: Mapped[str] = mapped_column(Text)
    """ B站用户名 """
    room_id: Mapped[Optional[str]] = mapped_column(String(64))
    """ B站直播间id """

    subscriptions: Mapped[List["SubscriptionRecord"]] = relationship(
        back_populates="user"
    )

    @property
    def bili_user(self) -> BiliUser:
        return BiliUser(uid=self.uid, name=self.name, room_id=self.room_id)


class SubscriptionRecord(Model):
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    target: Mapped[dict] = mapped_column(JSON)
    """ 发送目标 """
    live: Mapped[bool] = mapped_column(Boolean)
    """ 是否推送直播 """
    dynamic: Mapped[bool] = mapped_column(Boolean)
    """ 是否推送动态 """
    record: Mapped[bool] = mapped_column(Boolean)
    """ 是否录播 """

    user_id: Mapped[int] = mapped_column(ForeignKey("blive_biliuserrecord.id"))
    user: Mapped["BiliUserRecord"] = relationship(back_populates="subscriptions")

    @property
    def saa_target(self) -> PlatformTarget:
        return PlatformTarget.deserialize(self.target)

    @property
    def subscription(self) -> Subscription:
        return Subscription(
            target=self.saa_target,
            user=self.user.bili_user,
            options=SubscriptionOptions(
                live=self.live, dynamic=self.dynamic, record=self.record
            ),
        )
