from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    rss_update_cron: list = ['0', '*/5', '*', '*', '*', '*']
    rss_info_update_cron: list = ['0', '0', '5', '*', '*', '*']
