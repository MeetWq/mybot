from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosException
from config import *


class QCloudClient:
    def __init__(self, secret_id, secret_key, region, bucket):
        # 设置用户配置, 包括 secretId，secretKey 以及 Region
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.bucket = bucket
        self.config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
        self.client = CosS3Client(self.config)  # 获取客户端对象

    def upload_file(self, path, filename):
        url = None
        print(path)
        print(filename)
        try:
            self.client.upload_file(
                Bucket=self.bucket,
                LocalFilePath=path,
                Key=filename,
                PartSize=1,
                MAXThread=10,
                EnableMD5=False
            )
            url = self.config.uri(self.bucket, path=filename)
        except CosException:
            print('上传失败')
        return url


secret_id = qcloud_secret_id
secret_key = qcloud_secret_key
region = qcloud_region
bucket = qcloud_bucket
qcloud_client = QCloudClient(secret_id, secret_key, region, bucket)
