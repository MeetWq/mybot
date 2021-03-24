from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_petpet

export = export()
export.description = '摸头gif生成'
export.usage = 'Usage:\n  发送"摸摸我的头像"'
export.help = export.description + '\n' + export.usage

petpet = on_command('petpet', aliases={'摸摸我的头像'}, priority=24)


@petpet.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await petpet.send(message='请稍候...')
    user_id = event.user_id
    file_path = await get_petpet(user_id)
    if file_path:
        await petpet.send(message=MessageSegment.image(file='file://' + file_path))
        await petpet.finish()
    else:
        await petpet.finish('出错了，请稍后重试')
