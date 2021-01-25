from pydantic import BaseSettings


class Config(BaseSettings):
    cc98_user_name: str = ''
    cc98_user_password: str = ''

    class Config:
        extra = "ignore"
