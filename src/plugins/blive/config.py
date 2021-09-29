from pydantic import BaseSettings


class Config(BaseSettings):
    blive_cron_day: list = ['0', '*', '9-23', '*', '*', '*']
    blive_cron_night: list = ['0', '*/10', '0-8', '*', '*', '*']

    class Config:
        extra = "ignore"
