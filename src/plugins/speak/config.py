from pydantic import BaseSettings


class Config(BaseSettings):
    tencent_secret_id: str = ''
    tencent_secret_key: str = ''
    tts_project_id: str = ''

    class Config:
        extra = "ignore"
