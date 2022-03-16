import re
import random
from datetime import datetime, timedelta
from nonebot.matcher import Matcher
from nonebot.rule import to_me, Rule
from nonebot.permission import Permission
from nonebot.params import EventPlainText
from nonebot import get_driver, on_message
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)

from .data_source import chat_bot, get_anime_thesaurus
from .config import Config

chat_config = Config.parse_obj(get_driver().config.dict())


__des__ = "人工智障聊天"
__cmd__ = f"""
@我 进入连续对话模式，若{chat_config.chat_expire_time}s内无响应则结束对话，也可以发送“停、再见、闭嘴”结束对话
""".strip()
__short_cmd__ = "@我 聊天即可"
__usage__ = f"{__des__}\nUsage:\n{__cmd__}"


null_reply = ["怎么了？", "唔...怎么了？", "你好呀", "我在的"]

error_reply = ["这个问题我还不会", "我不知道该怎么回答", "其实我不太明白你的意思……"]

end_word = ["停", "爬", "滚", "stop", "结束", "再见", "闭嘴", "安静"]

filter_patterns = [
    r"^[\s,，.。?？!！/~$#@&^%+-_（）\\\(\)\*草艹哈h(卧槽)]+$",
    r"^[\.。/#\:].*",
    r"^&#91;\S+&#93;$",
    r"^&amp;#91;\S+&amp;#93;$",
    r"此处消息的转义尚未被插件支持",
    r"请使用最新版手机QQ体验新功能",
]


def filter_msg(msg: str = EventPlainText()):
    for p in filter_patterns:
        if re.search(p, msg):
            return False
    return True


chat = on_message(rule=to_me(), block=True, priority=100)


@chat.handle()
async def first_receive(
    matcher: Matcher, event: MessageEvent, msg: str = EventPlainText()
):
    if event.reply:
        await chat.finish()
    if not filter_msg(msg):
        await chat.finish()

    if msg:
        reply = await get_reply(msg, event)
    else:
        reply = random.choice(null_reply)

    await handle_reply(matcher, reply, event)


async def continue_receive(
    matcher: Matcher, event: MessageEvent, msg: str = EventPlainText()
):
    msg = msg.strip()
    if msg:
        for word in end_word:
            if word in msg.lower():
                await matcher.finish()
        if msg:
            reply = await get_reply(msg, event)
            await handle_reply(matcher, reply, event)


async def handle_reply(matcher: Matcher, reply: str, event: MessageEvent):
    if not reply:
        await matcher.finish()
    if isinstance(event, PrivateMessageEvent):
        await matcher.finish(reply)
    else:
        await matcher.send(reply)
        new_matcher(event)
        await matcher.finish()


def get_event_id(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return f"group_{event.group_id}"
    else:
        return f"private_{event.user_id}"


def new_matcher(event: MessageEvent):
    async def check_event_id(bot: Bot, new_event: MessageEvent) -> bool:
        return get_event_id(event) == get_event_id(new_event) and await chat.permission(
            bot, new_event
        )

    Matcher.new(
        chat.type,
        rule=Rule(filter_msg),
        permission=Permission(check_event_id),
        handlers=[continue_receive],
        temp=True,
        priority=chat.priority - 1,
        block=True,
        plugin=chat.plugin,
        module=chat.module,
        expire_time=datetime.now() + timedelta(seconds=chat_config.chat_expire_time),
    )


async def get_reply(msg: str, event: MessageEvent) -> str:
    prefix = event.group_id if isinstance(event, GroupMessageEvent) else "private"
    user_id = f"{prefix}_{event.user_id}"
    event_id = get_event_id(event)
    username = event.sender.card or event.sender.nickname or ""

    reply = await get_anime_thesaurus(msg)
    if reply:
        return reply

    reply = await chat_bot.get_reply(msg, event_id, user_id)
    if reply:
        return reply.replace("<USER-NAME>", username)
    return ""
