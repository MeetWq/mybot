from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    repeat_count: int = 2
