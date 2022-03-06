from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    mockingbird_ip: str = "localhost"
    mockingbird_port: str = "1234"
