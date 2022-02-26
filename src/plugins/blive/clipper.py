import httpx
import asyncio
import subprocess
from pathlib import Path
from threading import Thread
from datetime import datetime
from cachetools import TTLCache
from dataclasses import dataclass
from typing import Optional, Union, TYPE_CHECKING
from nonebot import get_driver
from nonebot.log import logger

from .sub_list import get_sub_list
from .uid_list import get_sub_info_by_uid
from .blrec import get_task, get_metadata
from .models import RunningStatus, LiveStatus
from .config import Config
from .send_msg import send_bot_msg

blive_config = Config.parse_obj(get_driver().config.dict())


@dataclass
class CutTask:
    user_id: str
    room_id: int
    file_path: Path
    start_time: float = 0
    stop_time: float = 0

    def start(self):
        self._thread = Thread(target=self.run)
        self._thread.start()
        logger.info(
            f"cut task {self.start_time} ~ {self.stop_time} of {self.file_path} start"
        )

    def run(self):
        self.out_path = self.file_path.parent / (
            self.file_path.stem
            + f" [{round(self.start_time)}~{round(self.stop_time)}].flv"
        )
        cmd = f"ffmpeg -ss {self.start_time} -t {self.stop_time - self.start_time} -i '{self.file_path}' -c copy '{self.out_path}'"
        popen = subprocess.Popen(cmd, shell=True)
        if popen.wait() != 0:
            logger.warning("f{cmd} run failed!")
            asyncio.get_event_loop().run_until_complete(
                send_bot_msg(self.user_id, "裁剪视频文件出错...")
            )
            return
        self.run_hooks()

    def run_hooks(self):
        for hook in blive_config.cut_file_webhooks:
            try:
                self.run_hook(hook)
            except:
                logger.warning(f"run hook {hook} failed!")

    def run_hook(self, url: str):
        logger.info(f"running hook {url}")
        data = {
            "id": self.user_id,
            "date": str(datetime.now()),
            "type": "CutFileCompletedEvent",
            "data": {"room_id": self.room_id, "path": str(self.out_path)},
        }
        httpx.post(url, json=data)
        logger.info(f"run hook {url} successfully")


if TYPE_CHECKING:
    cut_tasks: TTLCache[str, CutTask] = TTLCache(maxsize=100, ttl=60 * 60 * 1)
else:
    cut_tasks = TTLCache(maxsize=100, ttl=60 * 60 * 1)


def check_sub(user_id: str, uid: str) -> Optional[str]:
    sub_list = get_sub_list(user_id)
    if uid not in sub_list:
        return "尚未订阅该主播"
    if not sub_list[uid].get("record", False):
        return "未开启该主播的自动录播"


async def check_task(room_id: int) -> Union[str, Path]:
    task_info = await get_task(room_id)
    if not task_info:
        return "获取录播状态出错..."
    if task_info.room_info.live_status != LiveStatus.LIVE:
        return "该主播没有在直播..."
    if task_info.task_status.running_status != RunningStatus.RECORDING:
        return "获取录播状态出错..."
    path = task_info.task_status.recording_path
    if not path or not path.exists():
        return "检查录播文件出错..."
    return path


async def get_keyframe(room_id: int, offset: float) -> Union[str, float]:
    if offset < 0:
        return "偏移量只能是正数，指前向偏移，单位为秒"
    metadata = await get_metadata(room_id)
    if not metadata or not metadata.hasKeyframes:
        return "获取录播关键帧出错..."
    times = metadata.keyframes.times
    last_time = times[-1]
    time = last_time - offset
    if time > 0:
        time += max([t - time for t in times if t - time <= 0])
    else:
        time = 0
    return time


def task_key(user_id: str, uid: str):
    return f"{user_id}-{uid}"


async def cut_start(user_id: str, uid: str, offset: float) -> Optional[str]:
    if res := check_sub(user_id, uid):
        return res

    key = task_key(user_id, uid)
    if key in cut_tasks:
        return "当前有未结束的切片任务"

    room_id = int(get_sub_info_by_uid(uid)["room_id"])
    path = await check_task(room_id)
    if isinstance(path, str):
        return path

    time = await get_keyframe(room_id, offset)
    if isinstance(time, str):
        return time

    cut_tasks[key] = CutTask(user_id, room_id, file_path=path, start_time=time)
    return f"成功添加切片任务，切片开始时间：{round(time)}s"


async def cut_stop(user_id: str, uid: str, offset: float) -> Optional[str]:
    if res := check_sub(user_id, uid):
        return res

    key = task_key(user_id, uid)
    if key not in cut_tasks:
        return "不存在未结束的切片任务"

    room_id = int(get_sub_info_by_uid(uid)["room_id"])
    path = await check_task(room_id)
    if isinstance(path, str):
        return path

    if str(path.absolute()) != str(cut_tasks[key].file_path.absolute()):
        cut_tasks.pop(key)
        return "录播文件路径发生变动，切片失败..."

    time = await get_keyframe(room_id, offset)
    if isinstance(time, str):
        return time

    task = cut_tasks[key]
    if time <= task.start_time:
        return "切片结束时间必须大于开始时间！"
    if time - task.start_time <= 10:
        return "切片时长必须大于10s！"

    task.stop_time = time
    task.start()
    cut_tasks.pop(key)
    return f"切片结束时间：{round(time)}s，正在处理..."
