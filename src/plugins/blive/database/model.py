from typing import List, Optional

from nonebot_plugin_orm import Model, get_session
from nonebot_plugin_saa import PlatformTarget
from sqlalchemy import JSON, Boolean, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column

from ..models import BiliUser, Subscription, SubscriptionOptions


class BiliUserRecord(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(64))
    """ B站用户uid """
    name: Mapped[str] = mapped_column(Text)
    """ B站用户名 """
    room_id: Mapped[Optional[str]] = mapped_column(String(64))
    """ B站直播间id """

    @property
    def bili_user(self) -> BiliUser:
        return BiliUser(uid=self.uid, name=self.name, room_id=self.room_id)

    async def get_subscription_records(self) -> List["SubscriptionRecord"]:
        statement = select(SubscriptionRecord).where(
            SubscriptionRecord.user_id == self.id
        )
        async with get_session() as db_session:
            return list((await db_session.scalars(statement)).all())


class SubscriptionRecord(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    target: Mapped[dict] = mapped_column(JSON)
    """ 发送目标 """
    live: Mapped[bool] = mapped_column(Boolean)
    """ 是否推送直播 """
    dynamic: Mapped[bool] = mapped_column(Boolean)
    """ 是否推送动态 """
    record: Mapped[bool] = mapped_column(Boolean)
    """ 是否录播 """
    user_id: Mapped[int]
    """ 订阅用户id """

    @property
    def saa_target(self) -> PlatformTarget:
        return PlatformTarget.deserialize(self.target)

    async def get_user_record(self) -> Optional[BiliUserRecord]:
        async with get_session() as db_session:
            return await db_session.scalar(
                select(BiliUserRecord).where(BiliUserRecord.id == self.user_id)
            )

    async def subscription(self) -> Optional[Subscription]:
        if not (user_record := await self.get_user_record()):
            return

        return Subscription(
            target=self.saa_target,
            user=user_record.bili_user,
            options=SubscriptionOptions(
                live=self.live, dynamic=self.dynamic, record=self.record
            ),
        )
