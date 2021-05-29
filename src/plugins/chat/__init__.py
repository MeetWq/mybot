import random
from nonebot import export, on_message
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent, Message

from .data_source import chat_bot, get_anime_thesaurus

# export = export()
# export.description = '闲聊'
# export.usage = 'Usage:\n  智障对话'
# export.notice = 'Notice:\n  需要@我'
# export.help = export.description + '\n' + export.usage + '\n' + export.notice

chat = on_message(rule=to_me(), priority=39)

null_reply = [
    '怎么了？',
    '唔...怎么了？',
    '你好呀'
]


@chat.handle()
async def _(bot: Bot, event: Event, state: T_State):
    prefix = event.group_id if isinstance(
        event, GroupMessageEvent) else 'private'
    user_id = f'{prefix}_{event.user_id}'
    username = event.sender.card or event.sender.nickname
    state['user_id'] = user_id
    state['username'] = username

    msg = get_plain_text(event.get_message())
    reply = await get_reply(msg, user_id, username, new=True)
    if reply:
        await chat.send(reply)


@chat.got('msg')
async def _(bot: Bot, event: Event, state: T_State):
    user_id = state['user_id']
    username = state['username']
    msg = Message(state['msg'])
    msg = get_plain_text(msg)
    if not msg:
        await chat.finish()
    if len(msg) <= 1:
        await chat.reject()
    reply = await get_reply(msg, user_id, username)
    if reply:
        await chat.reject(reply)


def get_plain_text(msgs) -> str:
    msgs = [str(msg) for msg in msgs if msg.get('type') == 'text']
    return ' '.join(msgs).strip()


async def get_reply(msg: str, user_id: str, username: str, new: bool = False):
    if msg:
        reply = await get_anime_thesaurus(msg)
        if reply:
            return reply

        reply = await chat_bot.get_reply(msg, user_id, new)
        reply = reply.replace('<USER-NAME>', username)
        if reply:
            return reply

        return '其实我不太明白你的意思……'
    else:
        return random.choice(null_reply)
