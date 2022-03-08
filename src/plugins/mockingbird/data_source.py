import re
import cn2an
import httpx
import traceback
from io import BytesIO
from pathlib import Path
from typing import Optional, Union
from pydub import AudioSegment
from nonebot import get_driver
from nonebot.log import logger
from .config import Config

mb_config = Config.parse_obj(get_driver().config.dict())

dir_path = Path(__file__).parent / "resources"
with (dir_path / "recoder.wav").open("rb") as f:
    recoder = f.read()


def split_text(text: str):
    max_len = 50
    words = iter(re.split(r"[？！，。、?!,\.\n]+", text))
    lines = []
    current = next(words)
    for word in words:
        if len(current) + len(word) >= max_len:
            lines.append(current)
            current = word
        else:
            current += "\n" + word
    lines.append(current)
    return lines


async def get_voice(text: str) -> Optional[Union[str, BytesIO]]:
    url = (
        f"http://{mb_config.mockingbird_ip}:{mb_config.mockingbird_port}/api/synthesize"
    )
    files = {"file": recoder}
    try:
        texts = split_text(cn2an.transform(text, "an2cn"))
        sound = AudioSegment.silent(10)
        for t in texts:
            if len(t) > 50:
                return "连续文字过长，请用标点符号分割"
            data = {"text": t, "vocoder": "HifiGAN"}
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, data=data, files=files, timeout=20)
                result = resp.content
            sound += AudioSegment.from_file(BytesIO(result)) + AudioSegment.silent(200)
        output = BytesIO()
        sound.export(output, format="wav")
        return output
    except:
        logger.warning(traceback.format_exc())
        return None
