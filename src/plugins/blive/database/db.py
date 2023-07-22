from typing import List, Optional

from nonebot_plugin_datastore import create_session
from nonebot_plugin_saa import PlatformTarget
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import BiliUser, Subscription, SubscriptionOptions
from .model import BiliUserRecord, SubscriptionRecord


async def get_user_record(
    db_session: AsyncSession, uid: str
) -> Optional[BiliUserRecord]:
    statement = (
        select(BiliUserRecord)
        .where(BiliUserRecord.uid == uid)
        .options(selectinload(BiliUserRecord.subscriptions))
    )
    return await db_session.scalar(statement)


async def get_sub_record(
    db_session: AsyncSession, target: PlatformTarget, uid: str
) -> Optional[SubscriptionRecord]:
    if user := await get_user_record(db_session, uid):
        statement = (
            select(SubscriptionRecord)
            .where(
                SubscriptionRecord.target == target.dict(),
                SubscriptionRecord.user_id == user.id,
            )
            .options(selectinload(SubscriptionRecord.user))
        )
        return await db_session.scalar(statement)


async def get_user(uid: str) -> Optional[BiliUser]:
    async with create_session() as session:
        if record := await get_user_record(session, uid):
            return record.bili_user


async def get_users() -> List[BiliUser]:
    statement = select(BiliUserRecord)
    async with create_session() as session:
        return [record.bili_user for record in (await session.scalars(statement)).all()]


async def add_user(user: BiliUser):
    async with create_session() as session:
        if not await get_user_record(session, user.uid):
            record = BiliUserRecord(
                uid=user.uid,
                name=user.name,
                room_id=user.room_id,
            )
            session.add(record)
            await session.commit()


async def del_user(uid: str):
    async with create_session() as session:
        if record := await get_user_record(session, uid):
            if not record.subscriptions:
                await session.delete(record)
                await session.commit()


async def get_sub(target: PlatformTarget, uid: str) -> Optional[Subscription]:
    async with create_session() as session:
        if record := await get_sub_record(session, target, uid):
            return record.subscription


async def get_subs(target: PlatformTarget) -> List[Subscription]:
    statement = (
        select(SubscriptionRecord)
        .where(SubscriptionRecord.target == target.dict())
        .join(BiliUserRecord)
        .options(selectinload(SubscriptionRecord.user))
    )
    async with create_session() as session:
        return [
            record.subscription for record in (await session.scalars(statement)).all()
        ]


async def add_sub(subscription: Subscription):
    async with create_session() as session:
        if not (user := await get_user_record(session, subscription.user.uid)):
            user = BiliUserRecord(
                uid=subscription.user.uid,
                name=subscription.user.name,
                room_id=subscription.user.room_id,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        record = SubscriptionRecord(
            target=subscription.target.dict(),
            live=subscription.options.live,
            dynamic=subscription.options.dynamic,
            record=subscription.options.record,
            user_id=user.id,
        )
        session.add(record)
        await session.commit()


async def del_sub(target: PlatformTarget, uid: str):
    async with create_session() as session:
        if record := await get_sub_record(session, target, uid):
            await session.delete(record)
            await session.commit()
        if user := await get_user_record(session, uid):
            if not user.subscriptions:
                await session.delete(user)
                await session.commit()


async def update_user(user: BiliUser):
    async with create_session() as session:
        if record := await get_user_record(session, user.uid):
            record.name = user.name
            if user.room_id != None:
                record.room_id = user.room_id
            session.add(record)
            await session.commit()


async def update_sub_options(
    target: PlatformTarget, uid: str, options: SubscriptionOptions
):
    async with create_session() as session:
        if record := await get_sub_record(session, target, uid):
            record.live = options.live
            record.dynamic = options.dynamic
            record.record = options.record
            session.add(record)
            await session.commit()


async def get_uids() -> List[str]:
    statement = select(BiliUserRecord.uid)
    async with create_session() as session:
        return list((await session.scalars(statement)).all())


async def get_targets(uid: str) -> List[PlatformTarget]:
    async with create_session() as session:
        if user := await get_user_record(session, uid):
            return [sub.saa_target for sub in user.subscriptions]
        return []


async def get_live_uids() -> List[str]:
    statement = select(BiliUserRecord).options(
        selectinload(BiliUserRecord.subscriptions)
    )
    async with create_session() as session:
        users = (await session.scalars(statement)).all()
        return [
            user.uid for user in users if any((sub.live for sub in user.subscriptions))
        ]


async def get_live_targets(uid: str) -> List[PlatformTarget]:
    async with create_session() as session:
        if user := await get_user_record(session, uid):
            return [sub.saa_target for sub in user.subscriptions if sub.live]
        return []


async def get_dynamic_uids() -> List[str]:
    statement = select(BiliUserRecord).options(
        selectinload(BiliUserRecord.subscriptions)
    )
    async with create_session() as session:
        users = (await session.scalars(statement)).all()
        return [
            user.uid
            for user in users
            if any((sub.dynamic for sub in user.subscriptions))
        ]


async def get_dynamic_targets(uid: str) -> List[PlatformTarget]:
    async with create_session() as session:
        if user := await get_user_record(session, uid):
            return [sub.saa_target for sub in user.subscriptions if sub.dynamic]
        return []


async def get_record_uids() -> List[str]:
    statement = select(BiliUserRecord).options(
        selectinload(BiliUserRecord.subscriptions)
    )
    async with create_session() as session:
        users = (await session.scalars(statement)).all()
        return [
            user.uid
            for user in users
            if any((sub.record for sub in user.subscriptions))
        ]


async def get_record_targets(uid: str) -> List[PlatformTarget]:
    async with create_session() as session:
        if user := await get_user_record(session, uid):
            return [sub.saa_target for sub in user.subscriptions if sub.record]
        return []
