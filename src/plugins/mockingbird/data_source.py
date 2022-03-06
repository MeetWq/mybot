import httpx
import traceback
from io import BytesIO
from pathlib import Path
from typing import Optional
from pydub import AudioSegment
from nonebot import get_driver
from nonebot.log import logger
from .config import Config

mb_config = Config.parse_obj(get_driver().config.dict())

dir_path = Path(__file__).parent / "resources"


async def get_voice(text: str) -> Optional[BytesIO]:
    url = (
        f"http://{mb_config.mockingbird_ip}:{mb_config.mockingbird_port}/api/synthesize"
    )
    data = {"text": text, "vocoder": "HifiGAN"}
    files = {"file": (dir_path / "recoder.wav").open("rb")}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=data, files=files)
            result = resp.content
        sound = AudioSegment.from_file(BytesIO(result)) + AudioSegment.silent(300)
        output = BytesIO()
        sound.export(output, format="wav")
        return output
    except:
        logger.warning(traceback.format_exc())
        return None
