from pydantic import BaseSettings


class Config(BaseSettings):
    tencent_secret_id: str = ''
    tencent_secret_key: str = ''
    qcloud_region: str = ''
    qcloud_bucket: str = ''

    class Config:
        extra = "ignore"
