from pydantic import BaseSettings


class Config(BaseSettings):
    pixiv_token = ''

    class Config:
        extra = "ignore"
