import httpx
import shlex
import base64
import traceback
from typing import List, Optional
from dataclasses import dataclass, field

from nonebot import on_command
from nonebot.log import logger
from nonebot.rule import ArgumentParser
from nonebot.exception import ParserExit
from nonebot.params import CommandArg, Depends
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.adapters.onebot.v11.helpers import Cooldown, CooldownIsolateLevel

from .config import aidraw_config
from .data_source import txt2img, img2img

DEFUALT_PROMPT = (
    "((sfw)), masterpiece, best quality, extremely detailed CG unity 8k wallpaper, "
)
DEFUALT_NEGATIVE_PROMPT = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, "

cooldown = Cooldown(
    cooldown=aidraw_config.aidraw_cd,
    prompt="AI绘图冷却中……",
    isolate_level=CooldownIsolateLevel.GLOBAL,
)

parser = ArgumentParser("aidraw")
parser.add_argument("-p", "--shape", type=str, default="square", help="画布形状")
parser.add_argument("-c", "--scale", type=float, default=11, help="参数制约度")
parser.add_argument("-s", "--seed", type=int, default=-1, help="种子")
parser.add_argument("-r", "--strength", type=float, default=0.75, help="图生图相似度")
parser.add_argument("-t", "--steps", type=int, default=30, help="迭代次数")
parser.add_argument("-a", "--height", type=int, default=512, help="画布高度")
parser.add_argument("-w", "--width", type=int, default=512, help="画布宽度")
parser.add_argument("tags", nargs="*", default=[], help="描述标签")
parser.add_argument("-n", "--ntags", nargs="*", default=[], help="负面标签")


@dataclass
class Options:
    shape: str = "square"
    scale: float = 11
    seed: int = -1
    strength: float = 0.75
    steps: int = 30
    height: int = 512
    width: int = 512
    tags: List[str] = field(default_factory=list)
    ntags: List[str] = field(default_factory=list)


aidraw = on_command("aidraw", aliases={"ai绘图", "ai画图"}, priority=13, block=True)


def get_img_url():
    def dependency(event: MessageEvent):
        if event.reply:
            if imgs := event.reply.message["image"]:
                return imgs[0].data["url"]
        if imgs := event.message["image"]:
            return imgs[0].data["url"]
        if ats := event.message["at"]:
            return f"http://q1.qlogo.cn/g?b=qq&nk={ats[0].data['qq']}&s=640"
        return ""

    return Depends(dependency)


def get_img():
    async def dependency(img_url: str = get_img_url()):
        if not img_url:
            return None
        async with httpx.AsyncClient() as client:
            resp = await client.get(img_url, timeout=20)
            return resp.content

    return Depends(dependency)


@aidraw.handle([cooldown])
async def _(
    msg: Message = CommandArg(),
    img: Optional[bytes] = get_img(),
):
    msg_str = " ".join([str(seg) for seg in msg["text"]])
    try:
        argv = shlex.split(msg_str)
    except:
        await aidraw.finish("命令格式有误")

    try:
        args = parser.parse_args(argv)
    except ParserExit as e:
        await aidraw.finish(e.message)

    options = Options(**vars(args))

    shape = options.shape.lower()
    shape_dict = {
        "landscape": [512, 768],
        "portrait": [768, 512],
        "square": [512, 512],
    }
    if shape in shape_dict:
        height, width = shape_dict[shape]
    else:
        await aidraw.finish("画布形状格式不正确，应为 landscape, portrait, square 中的一个")

    height = options.height
    if height % 64 != 0:
        await aidraw.finish("图片高度应为 64 的整数倍")
    if height > 2048 or height < 64:
        await aidraw.finish("图片高度应在 64~2048 之间")

    width = options.width
    if width % 64 != 0:
        await aidraw.finish("图片宽度应为 64 的整数倍")
    if width > 2048 or width < 64:
        await aidraw.finish("图片宽度应在 64~2048 之间")

    steps = options.steps
    if steps > 150 or steps < 1:
        await aidraw.finish("迭代次数应为 1~150 的整数")

    scale = options.scale
    if scale > 30 or scale < 1:
        await aidraw.finish("参数制约度应在 1~30 之间")

    strength = options.strength
    if strength > 1 or strength < 0:
        await aidraw.finish("图生图相似度应在 0~1 之间")

    seed = options.seed
    prompt = DEFUALT_PROMPT + " ".join(options.tags)
    negative_prompt = DEFUALT_NEGATIVE_PROMPT + " ".join(options.ntags)

    res = ""
    try:
        if not img:
            res = await txt2img(
                prompt, negative_prompt, steps, scale, seed, height, width
            )
        else:
            img_b64 = f"data:image/png;base64,{base64.b64encode(img).decode()}"
            res = await img2img(
                prompt,
                negative_prompt,
                img_b64,
                steps,
                scale,
                strength,
                seed,
                height,
                width,
            )
    except:
        logger.warning(traceback.format_exc())

    if res:
        res_img = res.replace("data:image/png;base64,", "base64://", 1)
        await aidraw.finish(MessageSegment.image(res_img), at_sender=True)
    else:
        await aidraw.finish("生成失败，请稍后再试")
