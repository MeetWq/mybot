from pydantic import BaseSettings


class Config(BaseSettings):
    proxy = ''

    class Config:
        extra = "ignore"
