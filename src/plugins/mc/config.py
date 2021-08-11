from pydantic import BaseSettings


class Config(BaseSettings):
    dynmap_cron: list = ['*/20', '*', '*', '*', '*', '*']

    class Config:
        extra = "ignore"
