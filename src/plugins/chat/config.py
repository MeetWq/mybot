from pydantic import BaseSettings


class Config(BaseSettings):
    baidu_unit_api_key: str = ''
    baidu_unit_secret_key: str = ''
    baidu_unit_bot_id: str = ''
    chat_expire_time: int = 20

    class Config:
        extra = "ignore"
