from typing import List
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    bilibili_dynamic_cron: List[str] = ["0", "*", "*", "*", "*", "*"]
    blrec_ip: str = "localhost"
    blrec_port: str = "2233"
