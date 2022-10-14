import uuid
import httpx
import asyncio

from nonebot.log import logger

from .config import aidraw_config

aidraw_url = f"{aidraw_config.aidraw_api.strip('/')}/api/predict"


async def txt2img(
    prompt: str = "",
    negative_prompt: str = "",
    steps: int = 30,
    scale: float = 11,
    seed: int = -1,
    height: int = 512,
    width: int = 512,
) -> str:
    params = {
        "fn_index": 12,
        # fmt: off
        "data": [
            prompt, negative_prompt, "None", "None", steps, "DDIM", False, False, 1, 1, scale, seed, -1, 0, 0, 0, False, height, width, False, False, 0.7, "None", False, False, None, "", "Seed", "", "Steps", "", True, False, None, "", ""
        ],
        # fmt: on
        "session_hash": str(uuid.uuid4()),
    }
    return await post(params)


async def img2img(
    prompt: str = "",
    negative_prompt: str = "",
    img_b64: str = "",
    steps: int = 30,
    scale: float = 11,
    strength: float = 0.75,
    seed: int = -1,
    height: int = 512,
    width: int = 512,
) -> str:
    params = {
        "fn_index": 31,
        # fmt: off
        "data": [
            0, prompt, negative_prompt, "None", "None", img_b64, None, None, None, "Draw mask", steps, "Euler a", 4, "original", False, False, 1, 1, scale, strength, seed, -1, 0, 0, 0, False, height, width, "Crop and resize", False, 32, "Inpaint masked", "", "", "None", "", "", 1, 50, 0, False, 4, 1, '<p style="margin-bottom:0.75em">Recommended settings: Sampling Steps: 80-100, Sampler: Euler a, Denoising strength: 0.8</p>', 128, 8, ["left", "right", "up", "down"], 1, 0.05, 128, 4, "fill", ["left", "right", "up", "down"], False, False, None, "", '<p style="margin-bottom:0.75em">Will upscale the image to twice the dimensions; use width and height sliders to set tile size</p>', 64, "None", "Seed", "", "Steps", "", True, False, None, "", ""
        ],
        # fmt: on
        "session_hash": str(uuid.uuid4()),
    }
    return await post(params)


async def post(params: dict) -> str:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.post(
                    aidraw_url, json=params, timeout=60, follow_redirects=True
                )
                resp.raise_for_status()
                res = resp.json()
                return res["data"][0][0]
            except Exception as e:
                logger.warning(f"Error post aidraw, retry {i}/3: {e}")
                await asyncio.sleep(3)
    raise Exception("AI绘图请求失败")
