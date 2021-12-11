import io
import re
import json
import uuid
import httpx
import base64

import langid
from pydub import AudioSegment
from pydub.silence import detect_silence

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tts.v20190823 import tts_client, models

from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.cqhttp import MessageSegment

from .config import Config

global_config = get_driver().config
tts_config = Config(**global_config.dict())


async def get_voice(text, type=0):
    try:
        if langid.classify(text)[0] == 'ja':
            voice = await get_ai_voice(text, type)
        else:
            voice = await get_tx_voice(text, type)
        return voice
    except Exception as e:
        logger.warning(f'Error in get_voice({text}): {e}')
        return None


async def get_tx_voice(text, type=0):
    cred = credential.Credential(
        tts_config.tencent_secret_id, tts_config.tencent_secret_key)
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
    return MessageSegment.record(f"base64://{resp.Audio}")


async def get_ai_voice(text, type=0):
    mp3_url = await get_ai_voice_url(text, type)
    if not mp3_url:
        return None

    async with httpx.AsyncClient() as client:
        resp = await client.get(mp3_url)
        result = resp.content

    output = await split_voice(io.BytesIO(result))
    if output:
        return MessageSegment.record(f"base64://{base64.b64encode(output.getvalue()).decode()}")
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

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.text

    match_obj = re.search(r'"url":"(.*?)"', result)
    if match_obj:
        mp3_url = 'https:' + match_obj.group(1).replace('\/', '/')
        return mp3_url
    return ''


async def split_voice(input):
    sound = AudioSegment.from_file(input)
    silent_ranges = detect_silence(
        sound, min_silence_len=500, silence_thresh=-40)
    if len(silent_ranges) >= 1:
        first_silent_end = silent_ranges[0][1] - 300
        result = sound[first_silent_end:] + AudioSegment.silent(300)
        output = io.BytesIO()
        result.export(output, format='mp3')
        return output
    return None
