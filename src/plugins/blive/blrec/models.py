from datetime import datetime
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel


class LiveStatus(IntEnum):
    PREPARING = 0
    LIVE = 1
    ROUND = 2


class RoomInfo(BaseModel):
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


class UserInfo(BaseModel):
    name: str
    gender: str
    face: str
    uid: int


class BlrecEvent(BaseModel):
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
    data: dict[str, Any]


class LiveBeganEventData(BaseModel):
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


class RoomChangeEventData(BaseModel):
    room_info: RoomInfo


class RoomChangeEvent(BlrecEvent):
    type: Literal["RoomChangeEvent"]
    data: RoomChangeEventData


class RecordingStartedEventData(BaseModel):
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


class DiskUsage(BaseModel):
    total: int
    used: int
    free: int


class SpaceNoEnoughEventData(BaseModel):
    path: str
    threshold: int
    usage: DiskUsage


class SpaceNoEnoughEvent(BlrecEvent):
    type: Literal["SpaceNoEnoughEvent"]
    data: SpaceNoEnoughEventData


class ErrorData(BaseModel):
    name: str
    detail: str


class ErrorEvent(BlrecEvent):
    type: Literal["Error"]
    data: ErrorData


class UploaderEventData(BaseModel):
    room_id: int
    file_path: Path
    upload_dir: str
    share_url: str
    err_msg: str


class UploaderEvent(BaseModel):
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


class TaskStatus(BaseModel):
    monitor_enabled: bool
    recorder_enabled: bool
    running_status: RunningStatus


class TaskInfo(BaseModel):
    user_info: UserInfo
    room_info: RoomInfo
    task_status: TaskStatus
