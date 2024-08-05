from typing import Optional

from nonebot_plugin_orm import get_session
from nonebot_plugin_saa import PlatformTarget
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import BiliUser, Subscription, SubscriptionOptions
from .model import BiliUserRecord, SubscriptionRecord


async def get_user_record(
    db_session: AsyncSession, uid: int
) -> Optional[BiliUserRecord]:
    statement = select(BiliUserRecord).where(BiliUserRecord.uid == uid)
    return await db_session.scalar(statement)


async def get_sub_record(
    db_session: AsyncSession, target: PlatformTarget, uid: int
) -> Optional[SubscriptionRecord]:
    if user_record := await get_user_record(db_session, uid):
        statement = select(SubscriptionRecord).where(
            SubscriptionRecord.target == target.dict(),
            SubscriptionRecord.user_id == user_record.id,
        )
        return await db_session.scalar(statement)


async def get_user(uid: int) -> Optional[BiliUser]:
    async with get_session() as session:
        if user_record := await get_user_record(session, uid):
            return user_record.bili_user


async def get_users() -> list[BiliUser]:
    statement = select(BiliUserRecord)
    async with get_session() as session:
        return [record.bili_user for record in (await session.scalars(statement)).all()]


async def add_user(user: BiliUser):
    async with get_session() as session:
        if not await get_user_record(session, user.uid):
            user_record = BiliUserRecord(
                uid=user.uid,
                name=user.name,
                room_id=user.room_id,
            )
            session.add(user_record)
            await session.commit()


async def del_user(uid: int):
    async with get_session() as session:
        if user_record := await get_user_record(session, uid):
            if not await user_record.get_subscription_records():
                await session.delete(user_record)
                await session.commit()


async def get_sub(target: PlatformTarget, uid: int) -> Optional[Subscription]:
    async with get_session() as session:
        if sub_record := await get_sub_record(session, target, uid):
            return await sub_record.subscription()


async def get_subs(target: PlatformTarget) -> list[Subscription]:
    statement = select(SubscriptionRecord).where(
        SubscriptionRecord.target == target.dict()
    )
    subscriptions = []
    async with get_session() as session:
        records = (await session.scalars(statement)).all()
    for record in records:
        if subscription := await record.subscription():
            subscriptions.append(subscription)
    return subscriptions


async def add_sub(subscription: Subscription):
    async with get_session() as session:
        if not (user_record := await get_user_record(session, subscription.user.uid)):
            user_record = BiliUserRecord(
                uid=subscription.user.uid,
                name=subscription.user.name,
                room_id=subscription.user.room_id,
            )
            session.add(user_record)
            await session.commit()
            await session.refresh(user_record)
        record = SubscriptionRecord(
            target=subscription.target.dict(),
            live=subscription.options.live,
            dynamic=subscription.options.dynamic,
            record=subscription.options.record,
            user_id=user_record.id,
        )
        session.add(record)
        await session.commit()


async def del_sub(target: PlatformTarget, uid: int):
    async with get_session() as session:
        if sub_record := await get_sub_record(session, target, uid):
            await session.delete(sub_record)
            await session.commit()
        if user_record := await get_user_record(session, uid):
            if not await user_record.get_subscription_records():
                await session.delete(user_record)
                await session.commit()


async def update_user(user: BiliUser):
    async with get_session() as session:
        if user_record := await get_user_record(session, user.uid):
            user_record.name = user.name
            if user.room_id is not None:
                user_record.room_id = user.room_id
            session.add(user_record)
            await session.commit()


async def update_sub_options(
    target: PlatformTarget, uid: int, options: SubscriptionOptions
):
    async with get_session() as session:
        if sub_record := await get_sub_record(session, target, uid):
            sub_record.live = options.live
            sub_record.dynamic = options.dynamic
            sub_record.record = options.record
            session.add(sub_record)
            await session.commit()


async def get_uids() -> list[int]:
    statement = select(BiliUserRecord.uid)
    async with get_session() as session:
        return list((await session.scalars(statement)).all())


async def get_targets(uid: int) -> list[PlatformTarget]:
    async with get_session() as session:
        if user_record := await get_user_record(session, uid):
            return [
                record.saa_target
                for record in await user_record.get_subscription_records()
            ]
        return []


async def get_live_uids() -> list[int]:
    async with get_session() as session:
        user_records = (await session.scalars(select(BiliUserRecord))).all()
        return [
            user_record.uid
            for user_record in user_records
            if any(
                sub_record.live
                for sub_record in await user_record.get_subscription_records()
            )
        ]


async def get_live_targets(uid: int) -> list[PlatformTarget]:
    async with get_session() as session:
        if user_record := await get_user_record(session, uid):
            return [
                sub_record.saa_target
                for sub_record in await user_record.get_subscription_records()
                if sub_record.live
            ]
        return []


async def get_dynamic_uids() -> list[int]:
    async with get_session() as session:
        user_records = (await session.scalars(select(BiliUserRecord))).all()
        return [
            user_record.uid
            for user_record in user_records
            if any(
                sub_record.dynamic
                for sub_record in await user_record.get_subscription_records()
            )
        ]


async def get_dynamic_targets(uid: int) -> list[PlatformTarget]:
    async with get_session() as session:
        if user_record := await get_user_record(session, uid):
            return [
                sub_record.saa_target
                for sub_record in await user_record.get_subscription_records()
                if sub_record.dynamic
            ]
        return []


async def get_record_uids() -> list[int]:
    async with get_session() as session:
        user_records = (await session.scalars(select(BiliUserRecord))).all()
        return [
            user_record.uid
            for user_record in user_records
            if any(
                sub_record.record
                for sub_record in await user_record.get_subscription_records()
            )
        ]


async def get_record_targets(uid: int) -> list[PlatformTarget]:
    async with get_session() as session:
        if user_record := await get_user_record(session, uid):
            return [
                sub_record.saa_target
                for sub_record in await user_record.get_subscription_records()
                if sub_record.record
            ]
        return []
