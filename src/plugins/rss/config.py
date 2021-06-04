from pydantic import BaseSettings


class Config(BaseSettings):
    rss_update_cron: list = ['0', '*/5', '*', '*', '*', '*']
    rss_info_update_cron: list = ['0', '0', '5', '*', '*', '*']

    class Config:
        extra = "ignore"
