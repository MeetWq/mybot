from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg, EventToMe

from .config import Config
from .data_source import get_pixiv


__plugin_meta__ = PluginMetadata(
    name="pixiv",
    description="Pixiv搜图、排行榜",
    usage="pixiv {日榜/周榜/月榜/id/关键词}，关键词搜索需要 @我",
    config=Config,
    extra={
        "example": "pixiv 日榜\n@小Q pixiv 伊蕾娜",
    },
)


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
