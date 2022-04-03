import re
import json
import uuid
import httpx
import langid
import traceback
from io import BytesIO
from typing import Optional, Union
from pydub import AudioSegment
from pydub.silence import detect_silence

from tencentcloud.common import credential
from tencentcloud.tts.v20190823 import tts_client, models

from nonebot import get_driver
from nonebot.log import logger

from .config import Config

tts_config = Config.parse_obj(get_driver().config.dict())


async def get_voice(text, type=0) -> Optional[Union[str, BytesIO]]:
    try:
        if langid.classify(text)[0] == "ja":
            voice = await get_ai_voice(text, type)
        else:
            voice = await get_tx_voice(text, type)
        return voice
    except:
        logger.warning(traceback.format_exc())
        return None


async def get_tx_voice(text, type=0) -> str:
    cred = credential.Credential(
        tts_config.tencent_secret_id, tts_config.tencent_secret_key
    )
    client = tts_client.TtsClient(cred, "ap-shanghai")
    req = models.TextToVoiceRequest()

    if type == 0:
        voice_type = 101016
    else:
        voice_type = 101010

    params = {
        "Text": text,
        "SessionId": str(uuid.uuid1()),
        "Volume": 5,
        "Speed": 0,
        "ProjectId": int(tts_config.tts_project_id),
        "ModelType": 1,
        "VoiceType": voice_type,
    }
    req.from_json_string(json.dumps(params))
    resp = client.TextToVoice(req)
    return f"base64://{resp.Audio}"


async def get_ai_voice(text, type=0) -> Optional[BytesIO]:
    mp3_url = await get_ai_voice_url(text, type)
    if not mp3_url:
        return None

    async with httpx.AsyncClient() as client:
        resp = await client.get(mp3_url)
        result = resp.content

    return await split_voice(BytesIO(result))


async def get_ai_voice_url(text, type=0) -> str:
    url = "https://cloud.ai-j.jp/demo/aitalk_demo.php"
    if type == 0:
        params = {
            "callback": "callback",
            "speaker_id": 555,
            "text": text,
            "ext": "mp3",
            "volume": 2.0,
            "speed": 1,
            "pitch": 1,
            "range": 1,
            "webapi_version": "v5",
        }
    else:
        params = {
            "callback": "callback",
            "speaker_id": 1214,
            "text": text,
            "ext": "mp3",
            "volume": 2.0,
            "speed": 1,
            "pitch": 1,
            "range": 1,
            "anger": 0,
            "sadness": 0,
            "joy": 0,
            "webapi_version": "v5",
        }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.text

    match_obj = re.search(r'"url":"(.*?)"', result)
    if match_obj:
        mp3_url = "https:" + match_obj.group(1).replace(r"\/", "/")
        return mp3_url
    return ""


async def split_voice(input) -> Optional[BytesIO]:
    sound = AudioSegment.from_file(input)
    silent_ranges = detect_silence(sound, min_silence_len=500, silence_thresh=-40)
    if len(silent_ranges) >= 1:
        first_silent_end = silent_ranges[0][1] - 300
        result = sound[first_silent_end:] + AudioSegment.silent(300)
        output = BytesIO()
        result.export(output, format="mp3")
        return output
    return None
