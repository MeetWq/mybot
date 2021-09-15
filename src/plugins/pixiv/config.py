from pydantic import BaseSettings


class Config(BaseSettings):
    pixiv_token = ''
    saucenao_apikey = ''

    class Config:
        extra = "ignore"
