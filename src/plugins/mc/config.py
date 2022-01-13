from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    dynmap_cron: list = ['*/20', '*', '*', '*', '*', '*']
