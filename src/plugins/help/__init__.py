from nonebot import on_command, on_message
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import help_file_path

help_command = on_command('help', aliases={'帮助'}, rule=to_me(), priority=17)
help_at = on_message(rule=to_me(), priority=18, block=False)


async def send_help_img(event):
    await event.send(message=MessageSegment("image", {"file": "file://" + help_file_path()}))


@help_command.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await send_help_img(help_command)


@help_at.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    if not msg:
        await send_help_img(help_at)
