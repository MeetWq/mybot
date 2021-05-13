from pydantic import BaseSettings


class Config(BaseSettings):
    wolframalpha_appid = ''

    class Config:
        extra = "ignore"
