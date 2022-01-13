from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    bilibili_live_cron: list = ['0', '*', '*', '*', '*', '*']
    bilibili_dynamic_cron: list = ['0', '*', '*', '*', '*', '*']
    aliyunpan_refresh_token: str = ''
    aliyunpan_update_token_cron: list = ['0', '0', '6', '*', '*', '*']
