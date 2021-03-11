from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_sound

tts = on_command('speak', aliases={'说话'}, priority=14)
tts_at = on_command('说', rule=to_me(), priority=14)


@tts.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    await handle(tts, msg)


@tts_at.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    await handle(tts_at, msg)


async def handle(command, msg):
    if msg:
        file_path = await get_sound(msg)
        if file_path:
            await command.send(message=MessageSegment('record', {'file': 'file://' + file_path}))
            await command.finish()
        else:
            await command.finish('出错了，请稍后重试')
