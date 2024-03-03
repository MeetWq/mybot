from typing import List, Optional

import httpx

from ..config import blive_config
from ..database.db import get_record_uids, get_user
from .models import TaskInfo

BLREC_API = f"{blive_config.blrec_address}/api/v1"


async def get(url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=20)
        return resp.json()


async def post(url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, timeout=20)
        return resp.json()


async def delete(url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.delete(url, timeout=20)
        return resp.json()


async def get_tasks() -> List[TaskInfo]:
    url = f"{BLREC_API}/tasks/data?select=all"
    if result := await get(url):
        return [TaskInfo.model_validate(info) for info in result if info]
    return []


async def get_task(room_id: int) -> Optional[TaskInfo]:
    url = f"{BLREC_API}/tasks/{room_id}/data"
    if result := await get(url):
        return TaskInfo.model_validate(result)


async def add_task(room_id: int) -> bool:
    url = f"{BLREC_API}/tasks/{room_id}"
    result = await post(url)
    return result and result.get("code", -1) == 0


async def delete_task(room_id: int) -> bool:
    url = f"{BLREC_API}/tasks/{room_id}"
    result = await delete(url)
    return result and result.get("code", -1) == 0


async def enable_recorder(room_id: int) -> bool:
    url = f"{BLREC_API}/tasks/{room_id}/recorder/enable"
    result = await post(url)
    return result and result.get("code", -1) == 0


async def disable_recorder(room_id: int) -> bool:
    url = f"{BLREC_API}/tasks/{room_id}/recorder/disable"
    result = await post(url)
    return result and result.get("code", -1) == 0


async def sync_tasks():
    tasks = await get_tasks()
    task_uids = [task.user_info.uid for task in tasks]

    record_users = [await get_user(uid) for uid in await get_record_uids()]
    record_users = [user for user in record_users if user and user.room_id]
    record_uids = [user.uid for user in record_users]

    for task in tasks:
        if str(task.user_info.uid) not in record_uids:
            await delete_task(task.room_info.room_id)

    for user in record_users:
        uid = user.uid
        room_id = user.room_id
        assert room_id
        if uid not in task_uids:
            await add_task(room_id)
