from pydantic import BaseSettings


class Config(BaseSettings):
    setu_apikey: str = ''
    setu_group: list = []

    class Config:
        extra = "ignore"
