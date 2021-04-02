import os
import re
import json
import uuid
import base64
import aiohttp
import traceback
import subprocess
from pathlib import Path

import langid
from pydub import AudioSegment
from pydub.silence import detect_silence

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

cache_path = Path('cache/speak')
if not cache_path.exists():
    cache_path.mkdir(parents=True)


async def get_voice(text, type=0):
    try:
        if langid.classify(text)[0] == 'ja':
            voice_path = await get_ai_voice(text, type)
        else:
            voice_path = await get_tx_voice(text, type)
        return str(voice_path.absolute())
    except:
        logger.warning('Error in get_voice: ' + traceback.format_exc())
        return ''


async def get_tx_voice(text, type=0):
    cred = credential.Credential(tts_config.tencent_secret_id, tts_config.tencent_secret_key)
    http_profile = HttpProfile()
    http_profile.endpoint = 'tts.tencentcloudapi.com'
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client = tts_client.TtsClient(cred, 'ap-shanghai', client_profile)
    req = models.TextToVoiceRequest()

    if type == 0:
        voice_type = 101016
    elif type == 1:
        voice_type = 101010

    params = {
        'Text': text,
        'SessionId': str(uuid.uuid1()),
        'Volume': 5,
        'Speed': 0,
        'ProjectId': int(tts_config.tts_project_id),
        'ModelType': 1,
        'VoiceType': voice_type
    }
    req.from_json_string(json.dumps(params))
    resp = client.TextToVoice(req)

    file_name = uuid.uuid1().hex
    wav_path = cache_path / (file_name + '.wav')
    silk_path = cache_path / (file_name + '.silk')
    with wav_path.open('wb') as f:
        f.write(base64.b64decode(resp.Audio))

    if to_silk(wav_path, silk_path):
        return silk_path
    else:
        return None


async def get_ai_voice(text, type=0):
    file_name = uuid.uuid1().hex
    mp3_path = cache_path / (file_name + '.mp3')
    silk_path = cache_path / (file_name + '.silk')

    mp3_url = await get_ai_voice_url(text, type)
    if not mp3_url:
        return None

    async with aiohttp.ClientSession() as session:
        async with session.get(mp3_url) as resp:
            result = await resp.read()
    with mp3_path.open('wb') as f:
        f.write(result)

    if split_voice(mp3_path, mp3_path):
        if to_silk(mp3_path, silk_path):
            return silk_path
    return None


async def get_ai_voice_url(text, type=0):
    url = 'https://cloud.ai-j.jp/demo/aitalk_demo.php'
    if type == 0:
        params = {
            'callback': 'callback',
            'speaker_id': 555,
            'text': text,
            'ext': 'mp3',
            'volume': 2.0,
            'speed': 1,
            'pitch': 1,
            'range': 1,
            'webapi_version': 'v5'
        }
    elif type == 1:
        params = {
            'callback': 'callback',
            'speaker_id': 1214,
            'text': text,
            'ext': 'mp3',
            'volume': 2.0,
            'speed': 1,
            'pitch': 1,
            'range': 1,
            'anger': 0,
            'sadness': 0,
            'joy': 0,
            'webapi_version': 'v5'
        }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            result = await resp.text()
    match_obj = re.search(r'"url":"(.*?)"', result)
    if match_obj:
        mp3_url = 'https:' + match_obj.group(1).replace('\/', '/')
        return mp3_url
    return ''


def split_voice(input_path, output_path):
    sound = AudioSegment.from_mp3(str(input_path))
    silent_ranges = detect_silence(sound, min_silence_len=500, silence_thresh=-40)
    if len(silent_ranges) >= 1:
        first_silent_end = silent_ranges[0][1] - 300
        output = sound[first_silent_end:] + AudioSegment.silent(300)
        output.export(str(output_path), format="mp3")
        return True
    return False


def to_silk(input_path, output_path):
    stdout = open(os.devnull, 'w')
    p_open = subprocess.Popen('wx-voice encode -i {} -o {} -f silk'.format(input_path, output_path),
                              shell=True, stdout=stdout, stderr=stdout)
    p_open.wait()
    stdout.close()

    if p_open.returncode != 0:
        return False
    return True
