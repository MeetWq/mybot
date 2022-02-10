from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    rss_update_cron: list = ["0", "*/5", "*", "*", "*", "*"]

