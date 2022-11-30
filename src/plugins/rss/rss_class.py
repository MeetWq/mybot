import re
import time
import pytz
from typing import Union
from pytz import timezone
from datetime import datetime

TZ = timezone("Asia/Shanghai")
RSSHUB_PREFIX = "https://rsshub.app"


class RSS:
    def __init__(
        self,
        name: str,
        url: str,
        title: str = "",
        link: str = "",
        logo: str = "",
        rights: str = "",
        style: str = "main",
        last_update: Union[datetime, time.struct_time, str] = "",
    ):
        self.name = name
        self.url = self.parse_url(url, RSSHUB_PREFIX) if url else ""
        self.title = title
        self.link = link
        self.logo = logo
        self.rights = rights
        self.style = style
        self.last_update = (
            self.parse_time(last_update) if last_update else self.time_now()
        )

    @staticmethod
    def parse_url(url: str, base_url: str) -> str:
        if re.match(r"https?://", url, re.IGNORECASE):
            return url
        if url[0] == "/":
            url = base_url + url
        else:
            url = base_url + "/" + url
        return url

    @staticmethod
    def parse_time(raw_time: Union[datetime, time.struct_time, str]) -> datetime:
        if isinstance(raw_time, datetime):
            return raw_time.astimezone(TZ)
        elif isinstance(raw_time, time.struct_time):
            return (
                datetime.fromtimestamp(time.mktime(raw_time))
                .replace(tzinfo=pytz.utc)
                .astimezone(TZ)
            )
        elif isinstance(raw_time, str):
            return datetime.fromisoformat(raw_time).astimezone(TZ)

    @staticmethod
    def time_now() -> datetime:
        return datetime.now().astimezone(TZ)

    @classmethod
    def from_json(cls, json_dict: dict):
        name = json_dict.get("name", "")
        url = json_dict.get("url", "")
        title = json_dict.get("title", "")
        link = json_dict.get("link", "")
        logo = json_dict.get("logo", "")
        rights = json_dict.get("rights", "")
        style = json_dict.get("style", "main")
        last_update = json_dict.get("last_update")
        if last_update:
            last_update = datetime.fromisoformat(last_update)
        else:
            last_update = cls.time_now()
        return cls(
            name,
            url,
            title=title,
            link=link,
            logo=logo,
            rights=rights,
            style=style,
            last_update=last_update,
        )

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "title": self.title,
            "link": self.link,
            "logo": self.logo,
            "rights": self.rights,
            "style": self.style,
            "last_update": self.last_update.isoformat(),
        }
