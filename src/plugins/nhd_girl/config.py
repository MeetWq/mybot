from pydantic import BaseSettings


class Config(BaseSettings):
    nhd_group: list = []

    class Config:
        extra = "ignore"
