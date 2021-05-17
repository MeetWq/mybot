import random
from nonebot import export, on_message
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import call_tuling_api, get_anime_thesaurus

export = export()
export.description = '图灵机器人'
export.usage = 'Usage:\n  智障对话'
export.notice = 'Notice:\n  需要@我'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

tuling = on_message(rule=to_me(), priority=40)

null_reply = [
    '怎么了？',
    '唔...怎么了？',
    '你好呀'
]


@tuling.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    if msg:
        reply = await get_anime_thesaurus(msg)
        if reply:
            await tuling.finish(message=reply)

        user_id = event.get_user_id()
        reply = await call_tuling_api(msg, user_id)
        if reply:
            await tuling.finish(message=reply)

        await tuling.finish(message='其实我不太明白你的意思……')
    else:
        await tuling.finish(message=random.choice(null_reply))
