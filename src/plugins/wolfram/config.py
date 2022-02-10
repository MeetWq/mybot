from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    wolframalpha_appid = ""
