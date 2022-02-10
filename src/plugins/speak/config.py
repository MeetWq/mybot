from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    tencent_secret_id: str = ""
    tencent_secret_key: str = ""
    tts_project_id: str = ""
