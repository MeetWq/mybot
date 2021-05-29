from pydantic import BaseSettings


class Config(BaseSettings):
    baidu_unit_api_key: str = ''
    baidu_unit_secret_key: str = ''
    baidu_unit_bot_id: str = ''

    class Config:
        extra = "ignore"
