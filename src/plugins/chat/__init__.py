import re
import random
from datetime import datetime, timedelta
from nonebot import get_driver, on_message
from nonebot.permission import Permission
from nonebot.rule import to_me, Rule
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent, PrivateMessageEvent

from .data_source import chat_bot, get_anime_thesaurus
from .config import Config

global_config = get_driver().config
chat_config = Config(**global_config.dict())


__des__ = '人工智障聊天'
__cmd__ = '''
@我 进入连续对话模式，若15s内无响应则结束对话，也可以发送“停、再见、闭嘴”结束对话
'''.strip()
__short_cmd__ = '@我 聊天即可'
__usage__ = f'{__des__}\nUsage:\n{__cmd__}'


chat = on_message(rule=to_me(), priority=40)

null_reply = [
    '怎么了？',
    '唔...怎么了？',
    '你好呀',
    '我在的'
]

error_reply = [
    '这个问题我还不会',
    '我不知道该怎么回答',
    '其实我不太明白你的意思……'
]

end_word = [
    '停',
    '爬',
    '滚',
    'stop',
    '结束',
    '再见',
    '闭嘴',
    '安静'
]


@chat.handle()
async def first_receive(bot: Bot, event: Event, state: T_State):
    match_reply = re.search(r"\[CQ:reply,id=(-?\d*)]", event.raw_message)
    if match_reply:
        await chat.finish()

    msg = event.get_plaintext().strip()
    msg = filter_msg(msg)
    if msg:
        reply = await get_reply(msg, event)
    else:
        reply = random.choice(null_reply)

    await handle_reply(reply, event)


async def continue_receive(bot: Bot, event: Event, state: T_State):
    msg = event.get_plaintext().strip()
    msg = filter_msg(msg)
    if msg:
        for word in end_word:
            if word in msg.lower():
                await chat.finish()
        msg = filter_no_reply(msg)
        if msg:
            reply = await get_reply(msg, event)
            await handle_reply(reply, event)
    new_matcher(event)
    await chat.finish()


async def handle_reply(reply: str, event: Event):
    if not reply:
        await chat.finish()
    if isinstance(event, PrivateMessageEvent):
        await chat.finish(reply)
    else:
        await chat.send(reply)
        new_matcher(event)
        await chat.finish()


def get_event_id(event: Event):
    if isinstance(event, GroupMessageEvent):
        return f'group_{event.group_id}'
    else:
        return f'private_{event.user_id}'


def new_matcher(event: Event):
    async def check_event_id(bot: "Bot", new_event: "Event") -> bool:
        return get_event_id(event) == get_event_id(new_event) and await chat.permission(bot, new_event)

    Matcher.new(chat.type,
                Rule(),
                Permission(check_event_id),
                [continue_receive],
                temp=True,
                priority=chat.priority - 1,
                block=True,
                module=chat.module,
                expire_time=datetime.now() + timedelta(seconds=chat_config.chat_expire_time))


filter_patterns = [
    r'^[\s,，.。?？!！/~$#@&^%+-_（）\\\(\)\*]+$',
    r'^&#91;\S+&#93;$',
    r'^&amp;#91;\S+&amp;#93;$',
    r'此处消息的转义尚未被插件支持',
    r'请使用最新版手机QQ体验新功能'
]


def filter_msg(msg: str):
    for p in filter_patterns:
        if re.search(p, msg):
            return ''
    return msg


no_reply_patterns = [
    r'^[\s,，\.。?？!！/~$#@&^%+-_（）\\\(\)\*草艹哈h(卧槽)]+$',
    r'^[\.。/#\:].*'
]


def filter_no_reply(msg: str):
    for p in no_reply_patterns:
        if re.search(p, msg):
            return ''
    return msg


async def get_reply(msg: str, event: Event):
    prefix = event.group_id if isinstance(
        event, GroupMessageEvent) else 'private'
    user_id = f'{prefix}_{event.user_id}'
    event_id = get_event_id(event)
    username = event.sender.card or event.sender.nickname

    reply = await get_anime_thesaurus(msg)
    if reply:
        return reply

    reply = await chat_bot.get_reply(msg, event_id, user_id)
    reply = reply.replace('<USER-NAME>', username)
    if reply:
        return reply

    return random.choice(error_reply)
