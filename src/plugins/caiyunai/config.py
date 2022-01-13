from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    caiyunai_apikey: str = ''
