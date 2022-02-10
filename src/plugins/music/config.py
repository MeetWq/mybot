from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    tencent_secret_id: str = ""
    tencent_secret_key: str = ""
    qcloud_region: str = ""
    qcloud_bucket: str = ""
