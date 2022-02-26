import httpx
from typing import List, Optional
from nonebot import get_driver

from .config import Config
from .models import TaskInfo, MetaData
from .uid_list import get_record_users, get_sub_info_by_uid, get_sub_uids

blive_config = Config.parse_obj(get_driver().config.dict())
BLREC_API = f"http://{blive_config.blrec_ip}:{blive_config.blrec_port}/api/v1"


async def get_tasks() -> List[TaskInfo]:
    url = f"{BLREC_API}/tasks/data?select=all"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        result = resp.json()
    result = result or []
    tasks = [TaskInfo.parse_obj(info) for info in result if info]
    return tasks


async def get_task(room_id: int) -> Optional[TaskInfo]:
    url = f"{BLREC_API}/tasks/{room_id}/data"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        result = resp.json()
    return TaskInfo.parse_obj(result) if result else None


async def get_metadata(room_id: int) -> Optional[MetaData]:
    url = f"{BLREC_API}/tasks/{room_id}/metadata"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        result = resp.json()
    return MetaData.parse_obj(result) if result else None


async def add_task(room_id: int) -> bool:
    url = f"{BLREC_API}/tasks/{room_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url)
        result = resp.json()
    return result and result.get("code", -1) == 0


async def delete_task(room_id: int) -> bool:
    url = f"{BLREC_API}/tasks/{room_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.delete(url)
        result = resp.json()
    return result and result.get("code", -1) == 0


async def enable_recorder(room_id: int) -> bool:
    url = f"{BLREC_API}/tasks/{room_id}/recorder/enable"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url)
        result = resp.json()
    return result and result.get("code", -1) == 0


async def disable_recorder(room_id: int) -> bool:
    url = f"{BLREC_API}/tasks/{room_id}/recorder/disable"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url)
        result = resp.json()
    return result and result.get("code", -1) == 0


async def sync_tasks():
    tasks = await get_tasks()
    sub_task_uids = [task.user_info.uid for task in tasks]
    rec_task_uids = [
        task.user_info.uid for task in tasks if task.task_status.recorder_enabled
    ]
    sub_uids = get_sub_uids()

    for task in tasks:
        if str(task.user_info.uid) not in sub_uids:
            await delete_task(task.room_info.room_id)

    for uid in sub_uids:
        room_id = get_sub_info_by_uid(uid)["room_id"]
        if uid not in sub_task_uids:
            await add_task(room_id)
            await disable_recorder(room_id)
        if get_record_users(uid):
            await enable_recorder(room_id)
        elif uid in rec_task_uids:
            await disable_recorder(room_id)
