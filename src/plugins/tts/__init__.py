from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_sound

tts = on_command('speak', aliases={'说话'}, priority=14)


@tts.handle()
@tts.args_parser
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    if msg:
        file_path = await get_sound(msg)
        if file_path:
            await tts.send(message=MessageSegment('record', {'file': 'file://' + file_path}))
            await tts.finish()
        else:
            await tts.finish('出错了，请稍后重试')
