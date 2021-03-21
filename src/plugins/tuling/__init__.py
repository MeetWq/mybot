from nonebot import export, on_message
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event

from .data_source import call_tuling_api

export = export()
export.description = '图灵机器人'
export.usage = 'Usage:\n  智障对话'
export.notice = 'Notice:\n  需要@我；图灵优先级为最低'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

tuling = on_message(rule=to_me(), priority=40)


@tuling.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    if msg:
        user_id = event.get_user_id()
        reply = await call_tuling_api(msg, user_id)
        if reply:
            await tuling.send(message=reply)
        else:
            await tuling.send(message='其实我不太明白你的意思……')
