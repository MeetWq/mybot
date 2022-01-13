from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosException
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

qcloud_config = Config.parse_obj(get_driver().config.dict())


class QCloudClient:
    def __init__(self):
        self.secret_id = qcloud_config.tencent_secret_id
        self.secret_key = qcloud_config.tencent_secret_key
        self.region = qcloud_config.qcloud_region
        self.bucket = qcloud_config.qcloud_bucket
        self.config = CosConfig(
            Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key)
        self.client = CosS3Client(self.config)

    def put_object(self, stream, filename) -> str:
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Body=stream,
                Key=filename,
                EnableMD5=False
            )
            url = self.config.uri(self.bucket, path=filename)
            return url
        except CosException:
            logger.warning('upload file to qcloud cos failed: ' + filename)
            return ''
