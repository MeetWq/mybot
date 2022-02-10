import re
from typing import Union
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, EventToMe, Arg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from .data_source import get_pixiv, search_by_image


__des__ = "Pixiv图片、以图搜图"
__cmd__ = """
1. pixiv {日榜/周榜/月榜/id/关键词}，关键词搜索需要 @我
2. 搜图 {图片/url}
""".strip()
__example__ = """
pixiv 日榜
@小Q pixiv 伊蕾娜
""".strip()
__usage__ = f"{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}"


pixiv = on_command("pixiv", block=True, priority=12)


@pixiv.handle()
async def _(msg: Message = CommandArg(), tome: bool = EventToMe()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        await pixiv.finish()

    if not keyword.isdigit() and keyword not in ["日榜", "周榜", "月榜"]:
        if not tome:
            await pixiv.finish()

    res = await get_pixiv(keyword)
    if not res:
        await pixiv.finish("出错了，请稍后再试")
    await pixiv.finish(res)


pic_search = on_command("搜图", block=True, priority=14)


@pic_search.handle()
async def _(matcher: Matcher, event: MessageEvent, msg: Message = CommandArg()):
    if event.reply:
        reply = event.reply.message
        if parse_url(reply):
            matcher.set_arg("img_url", reply)
    else:
        matcher.set_arg("img_url", msg)


@pic_search.got("img_url", prompt="请发送一张图片或图片链接")
async def _(img_url: Union[str, Message] = Arg()):
    img_url = parse_url(img_url)
    if not img_url:
        await pic_search.reject()
    msg = await search_by_image(img_url)
    if not msg:
        await pic_search.finish("出错了，请稍后再试")
    await pic_search.finish(msg)


def parse_url(msg: Union[str, Message]):
    img_url = ""
    if isinstance(msg, Message):
        for msg_seg in msg:
            if msg_seg.type == "image":
                img_url = msg_seg.data["url"]
            elif msg_seg.type == "text":
                text: str = msg_seg.data["text"]
                if text.startswith("http"):
                    img_url = text.split()[0]
    elif isinstance(msg, str):
        if msg.startswith("http"):
            img_url = msg.split()[0]
        else:
            match = re.search(r"\[CQ:image.*?url=(.*?)\]", msg)
            if match:
                img_url = match.group(1)
    return img_url
