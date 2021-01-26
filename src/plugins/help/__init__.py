import os
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

dir_path = os.path.split(os.path.realpath(__file__))[0]

help = on_command('help', aliases={'帮助'}, rule=to_me(), priority=12)


@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    file_path = os.path.join(dir_path, 'help.png')
    await help.send(message=MessageSegment("image", {"file": "file://" + file_path}))
