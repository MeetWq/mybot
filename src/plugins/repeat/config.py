from pydantic import BaseSettings


class Config(BaseSettings):
    repeat_count: int = 2

    class Config:
        extra = "ignore"
