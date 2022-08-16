from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .data_source import get_random_pic

picbank = on_command("抽", aliases={"来个"}, block=False, priority=14)


keyword_dict = {
    "阿准": ["阿准"],
    "艾萌": ["艾萌"],
    "兰枫": ["兰枫"],
    "璃亚": ["璃亚", "ria"],
    "南莓": ["南莓", "小南莓"],
    "南小科": ["南小科"],
    "桃子": ["桃子"],
    "团子": ["团子"],
    "夏樱": ["夏樱", "夏嘤"],
    "小科": ["小科", "野猪", "🐗"],
    "樱花小帮": ["樱花小帮", "小帮"],
    "樱桃": ["樱桃"],
}


@picbank.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    for dir_name, keywords in keyword_dict.items():
        if keyword.lower() in keywords:
            res = get_random_pic(dir_name)
            if res:
                matcher.stop_propagation()
                await picbank.finish(MessageSegment.image(res.read_bytes()))
