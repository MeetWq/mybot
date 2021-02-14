from pydantic import BaseSettings


class Config(BaseSettings):
    cherria_group: list = []

    class Config:
        extra = "ignore"
