from typing import List
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    bilibili_dynamic_cron: List[str] = ["0", "*", "*", "*", "*", "*"]
    blrec_address: str = "http://your_address"
    bilibili_cookie: str = ""
