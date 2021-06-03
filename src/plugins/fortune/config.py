from pydantic import BaseSettings


class Config(BaseSettings):
    fortune_style: str = 'summer'

    class Config:
        extra = 'ignore'
