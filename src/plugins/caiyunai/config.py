from pydantic import BaseSettings


class Config(BaseSettings):
    caiyunai_apikey: str = ''

    class Config:
        extra = "ignore"
