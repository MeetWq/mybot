from datetime import datetime

from nonebot_plugin_orm import Model
from sqlalchemy import TEXT, String
from sqlalchemy.orm import Mapped, mapped_column


class MessageRecord(Model):
    """消息记录"""

    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[datetime]
    """ 消息时间 """
    account: Mapped[str] = mapped_column(String(64))
    """ 用户名 """
    message: Mapped[str] = mapped_column(TEXT)
    """ 消息内容 """
