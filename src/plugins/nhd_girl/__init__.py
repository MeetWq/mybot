import random
import re

from nonebot import on_message, require
from nonebot.matcher import Matcher
from nonebot.params import EventPlainText
from nonebot.rule import Rule
from nonebot.typing import T_State

require("nonebot_plugin_uninfo")

from nonebot_plugin_uninfo import Uninfo

entries: dict[str, list[str]] = {
    r"[Nn][Hh][Dd]娘[ ,，]*求交往": [
        "你是个好人，这张好人卡请收下吧~",
    ],
    r"[Nn][Hh][Dd]娘[ ,，]*求约会": [
        "才不要呢！约会什么的最讨厌了！",
        "好的 {nickname}，三分钟后来八舍楼下等我哦！",
    ],
    r"[Nn][Hh][Dd]娘[ ,，]*(你|早上|晚上|中午|下午)好": [
        "你好~今天NHD娘也是活力满满地在工作着呢！",
        "你好~这里是最勤劳最可爱的NHD娘~",
        "你……你好！呜！被看到没睡醒的样子了>_<",
    ],
    r"[Nn][Hh][Dd]娘[ ,，]*(求|我要)米": [
        "哼！人家才不知道什么叫米呢！",
        "求米什么的最讨厌了！烦死了烦死了烦死了！",
        "呜呜，为什么你们这些人总是米米米的，人家弄不懂啦~",
        "呵呵，你们不知道，我跟马爷谈笑风生，你们这些求米的人啊，naive！",
    ],
    r"[Nn][Hh][Dd]娘[ ,，]*(马爷|麻耶)": [
        "你说的是 sssdjay 吗？马爷可是永远的博士之光呢！NHD娘最喜欢他了！嗯嗯！",
    ],
}


def nhd_girl_rule() -> Rule:
    def checker(state: T_State, message: str = EventPlainText()) -> bool:
        if not message:
            return False
        for pattern, replies in entries.items():
            if re.fullmatch(pattern, message):
                reply = random.choice(replies)
                state["reply"] = reply
                return True
        return False

    return Rule(checker)


nhd_girl = on_message(nhd_girl_rule(), block=True, priority=15)


@nhd_girl.handle()
async def _(matcher: Matcher, state: T_State, session: Uninfo):
    reply: str = state["reply"]
    username = session.user.nick or session.user.name or ""
    if session.member and session.member.nick:
        username = session.member.nick
    reply = reply.format(nickname=username)
    await matcher.finish(reply)
