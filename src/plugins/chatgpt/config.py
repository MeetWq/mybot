from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatgpt_session_token: str = ""
    http_proxy: str = ""
