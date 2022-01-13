from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    cc98_user_name: str = ''
    cc98_user_password: str = ''
