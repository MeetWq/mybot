from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    fortune_style: str = 'summer'
