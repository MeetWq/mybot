from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_voice

tts = on_command('speak', aliases={'说话'}, priority=14)
tts_at = on_command('说', rule=to_me(), priority=15)


@tts.handle()
@tts_at.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    if msg:
        await tts.send(message='请稍候...')
        file_path = await get_voice(msg)
        if file_path:
            await tts.send(message=MessageSegment('record', {'file': 'file://' + file_path}))
            await tts.finish()
        else:
            await tts.finish('出错了，请稍后重试')
