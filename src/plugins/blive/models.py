import time
from enum import Enum, IntEnum
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union
from pydantic import BaseModel, Extra
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .data_source import get_dynamic_screenshot


class LiveStatus(IntEnum):
    PREPARING = 0
    LIVE = 1
    ROUND = 2


class RoomInfo(BaseModel, extra=Extra.ignore):
    uid: int
    room_id: int
    short_room_id: int
    area_id: int
    area_name: str
    parent_area_id: int
    parent_area_name: str
    live_status: LiveStatus
    live_start_time: int
    online: int
    title: str
    cover: str
    tags: str
    description: str


class UserInfo(BaseModel, extra=Extra.ignore):
    name: str
    gender: str
    face: str
    uid: int
    level: int
    sign: str


class BlrecEvent(BaseModel, extra=Extra.ignore):
    id: str
    date: datetime
    type: Literal[
        "LiveBeganEvent",
        "LiveEndedEvent",
        "RoomChangeEvent",
        "RecordingStartedEvent",
        "RecordingFinishedEvent",
        "RecordingCancelledEvent",
        "VideoFileCreatedEvent",
        "VideoFileCompletedEvent",
        "DanmakuFileCreatedEvent",
        "DanmakuFileCompletedEvent",
        "RawDanmakuFileCreatedEvent",
        "RawDanmakuFileCompletedEvent",
        "VideoPostprocessingCompletedEvent",
        "SpaceNoEnoughEvent",
        "Error",
    ]
    data: Dict[str, Any]


class LiveBeganEventData(BaseModel, extra=Extra.ignore):
    user_info: UserInfo
    room_info: RoomInfo


class LiveEndedEventData(LiveBeganEventData):
    pass


class LiveBeganEvent(BlrecEvent):
    type: Literal["LiveBeganEvent"]
    data: LiveBeganEventData


class LiveEndedEvent(BlrecEvent):
    type: Literal["LiveEndedEvent"]
    data: LiveEndedEventData


class RoomChangeEventData(BaseModel, extra=Extra.ignore):
    room_info: RoomInfo


class RoomChangeEvent(BlrecEvent):
    type: Literal["RoomChangeEvent"]
    data: RoomChangeEventData


class RecordingStartedEventData(BaseModel, extra=Extra.ignore):
    room_info: RoomInfo


class RecordingStartedEvent(BlrecEvent):
    type: Literal["RecordingStartedEvent"]
    data: RecordingStartedEventData


class RecordingFinishedEventData(RecordingStartedEventData):
    pass


class RecordingFinishedEvent(BlrecEvent):
    type: Literal["RecordingFinishedEvent"]
    data: RecordingFinishedEventData


class RecordingCancelledEventData(RecordingStartedEventData):
    pass


class RecordingCancelledEvent(BlrecEvent):
    type: Literal["RecordingCancelledEvent"]
    data: RecordingCancelledEventData


class DiskUsage(BaseModel, extra=Extra.ignore):
    total: int
    used: int
    free: int


class SpaceNoEnoughEventData(BaseModel, extra=Extra.ignore):
    path: str
    threshold: int
    usage: DiskUsage


class SpaceNoEnoughEvent(BlrecEvent):
    type: Literal["SpaceNoEnoughEvent"]
    data: SpaceNoEnoughEventData


class ErrorData(BaseModel, extra=Extra.ignore):
    name: str
    detail: str


class ErrorEvent(BlrecEvent):
    type: Literal["Error"]
    data: ErrorData


class UploaderEventData(BaseModel, extra=Extra.ignore):
    room_id: int
    file_path: Path
    upload_dir: str
    share_url: str
    err_msg: str


class UploaderEvent(BaseModel, extra=Extra.ignore):
    id: str
    date: datetime
    type: Literal["UploadCompleted"]
    data: UploaderEventData


class RunningStatus(str, Enum):
    STOPPED = "stopped"
    WAITING = "waiting"
    RECORDING = "recording"
    REMUXING = "remuxing"
    INJECTING = "injecting"


QualityNumber = Literal[
    20000,  # 4K
    10000,  # 原画
    401,  # 蓝光(杜比)
    400,  # 蓝光
    250,  # 超清
    150,  # 高清
    80,  # 流畅
]


class TaskStatus(BaseModel, extra=Extra.ignore):
    monitor_enabled: bool
    recorder_enabled: bool
    running_status: RunningStatus


class TaskInfo(BaseModel, extra=Extra.ignore):
    user_info: UserInfo
    room_info: RoomInfo
    task_status: TaskStatus


class Dynamic:
    def __init__(self, dynamic: dict):
        self.dynamic = dynamic
        self.type = dynamic["desc"]["type"]
        self.id = dynamic["desc"]["dynamic_id"]
        self.time = dynamic["desc"]["timestamp"]
        self.uid = dynamic["desc"]["user_profile"]["info"]["uid"]
        self.name = dynamic["desc"]["user_profile"]["info"].get("uname")

    async def format_msg(self) -> Optional[Message]:
        img = await get_dynamic_screenshot(self.id)
        if not img:
            return None
        type_msg = {
            0: "发布了新动态",
            1: "转发了一条动态",
            8: "发布了新投稿",
            16: "发布了短视频",
            64: "发布了新专栏",
            256: "发布了新音频",
        }
        msg = Message()
        msg.append(f"{self.name} {type_msg.get(self.type, type_msg[0])}:")
        msg.append(MessageSegment.image(img))
        return msg


class LiveInfo:
    def __init__(self, user_info: UserInfo, room_info: RoomInfo):
        self.up_name = user_info.name
        self.status = room_info.live_status
        self.time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(room_info.live_start_time)
        )
        self.url = f"https://live.bilibili.com/{room_info.room_id}"
        self.title = room_info.title
        self.cover = room_info.cover

    async def format_msg(self) -> Optional[Union[str, Message]]:
        msg = None
        if self.status == LiveStatus.LIVE:
            msg = Message()
            msg.append(
                f"{self.time}\n"
                f"{self.up_name} 开播啦！\n"
                f"{self.title}\n"
                f"直播间链接：{self.url}"
            )
            msg.append(MessageSegment.image(self.cover))
            return msg
        elif self.status == LiveStatus.PREPARING:
            return f"{self.up_name} 下播了"
        elif self.status == LiveStatus.ROUND:
            return f"{self.up_name} 下播了（轮播中）"
