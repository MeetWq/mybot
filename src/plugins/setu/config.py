from pydantic import BaseSettings


class Config(BaseSettings):
    setu_apikey: str = ''

    class Config:
        extra = "ignore"
