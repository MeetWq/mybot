from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    bili_user1_cookie: str = ""
    bili_user2_cookie: str = ""
