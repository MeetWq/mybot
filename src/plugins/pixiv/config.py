from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    pixiv_token = ""
    saucenao_apikey = ""
