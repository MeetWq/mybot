from pydantic import BaseSettings


class Config(BaseSettings):
    bilibili_live_cron: list = ['0', '*', '*', '*', '*', '*']
    bilibili_dynamic_cron: list = ['0', '*', '*', '*', '*', '*']
    aliyunpan_refresh_token: str = ''

    class Config:
        extra = "ignore"
