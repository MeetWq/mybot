from pydantic import BaseSettings


class Config(BaseSettings):
    pixiv_token = ''
    tencent_secret_id = ''
    tencent_secret_key = ''

    class Config:
        extra = "ignore"
