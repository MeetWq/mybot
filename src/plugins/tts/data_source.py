import os
import json
import uuid
import base64
import traceback
import subprocess
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tts.v20190823 import tts_client, models

from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
tts_config = Config(**global_config.dict())
dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)


async def get_sound(text):
    try:
        cred = credential.Credential(tts_config.tencent_secret_id, tts_config.tencent_secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = 'tts.tencentcloudapi.com'
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = tts_client.TtsClient(cred, 'ap-shanghai', client_profile)
        req = models.TextToVoiceRequest()
        params = {
            'Text': text,
            'SessionId': str(uuid.uuid1()),
            'Volume': 5,
            'Speed': 0,
            'ProjectId': int(tts_config.tts_project_id),
            'ModelType': 1,
            'VoiceType': 101016
        }
        req.from_json_string(json.dumps(params))
        resp = client.TextToVoice(req)

        wav_path = os.path.join(cache_path, 'tmp.wav')
        silk_path = os.path.join(cache_path, 'tmp.silk')
        with open(wav_path, 'wb') as f:
            f.write(base64.b64decode(resp.Audio))

        if to_silk(wav_path, silk_path):
            return silk_path
        else:
            return ''

    except TencentCloudSDKException:
        logger.warning('Error in get sound: ' + traceback.format_exc())
        return ''


def to_silk(input_path, output_path):
    stdout = open(os.devnull, 'w')
    p_open = subprocess.Popen('wx-voice encode -i {} -o {} -f silk'.format(input_path, output_path),
                              shell=True, stdout=stdout, stderr=stdout)
    p_open.wait()
    stdout.close()

    if p_open.returncode != 0:
        return False
    return True
