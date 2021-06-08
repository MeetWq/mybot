import random
from nonebot import export, on_message
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent, PrivateMessageEvent, Message

from .data_source import chat_bot, get_anime_thesaurus

export = export()
export.description = '闲聊'
export.usage = 'Usage:\n  和我对话即可，第一次需要@我触发，若30s无响应则结束对话'
export.notice = 'Notice:\n  对话是一对一的，不能插话'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

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
    '停下',
    '停停',
    '停一停',
    '爬'
    'stop',
    '结束',
    '结束对话',
    '结束会话',
    '再见'
]


@chat.handle()
async def _(bot: Bot, event: Event, state: T_State):
    prefix = event.group_id if isinstance(
        event, GroupMessageEvent) else 'private'
    user_id = f'{prefix}_{event.user_id}'
    username = event.sender.card or event.sender.nickname
    state['user_id'] = user_id
    state['username'] = username

    msg = event.get_plaintext().strip()
    reply = await get_reply(msg, user_id, username)
    if reply:
        if isinstance(event, PrivateMessageEvent):
            await chat.finish(reply)
        else:
            await chat.send(reply)


@chat.got('msg')
async def _(bot: Bot, event: Event, state: T_State):
    user_id = state['user_id']
    username = state['username']
    msg = Message(state['msg'])
    msg = get_plain_text(msg)
    if not msg:
        await chat.reject()
    if msg in end_word:
        await chat.finish()
    reply = await get_reply(msg, user_id, username)
    if reply:
        await chat.reject(reply)


def get_plain_text(msgs) -> str:
    msgs = [str(msg) for msg in msgs if msg.get('type') == 'text']
    return ' '.join(msgs).strip()


async def get_reply(msg: str, user_id: str, username: str):
    if msg:
        reply = await get_anime_thesaurus(msg)
        if reply:
            return reply

        reply = await chat_bot.get_reply(msg, user_id)
        reply = reply.replace('<USER-NAME>', username)
        if reply:
            return reply

        return random.choice(error_reply)
    else:
        return random.choice(null_reply)
