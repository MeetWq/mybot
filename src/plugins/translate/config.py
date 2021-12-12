from pydantic import BaseSettings


class Config(BaseSettings):
    baidu_trans_app_id: str = ''
    baidu_trans_api_key: str = ''
    youdao_trans_app_id: str = ''
    youdao_trans_api_key: str = ''
    google_trans_api_key: str = ''
    bing_trans_region: str = ''
    bing_trans_api_key: str = ''

    class Config:
        extra = "ignore"
