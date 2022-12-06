from typing import Optional
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    baidu_unit_api_key: str = ""
    baidu_unit_secret_key: str = ""
    baidu_unit_bot_id: str = ""
    chatgpt_session_token: str = ""
    chat_expire_time: int = 20
    http_proxy: Optional[str] = None
