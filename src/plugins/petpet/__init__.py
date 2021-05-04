from nonebot import export, on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment

from .data_source import get_petpet

export = export()
export.description = '摸头gif生成'
export.usage = 'Usage:\n  摸摸 [@user]'
export.notice = 'Notice:\n  没有@人则使用发送者的头像'
export.help = export.description + '\n' + export.usage + '\n' + export.notice

petpet = on_command('petpet', aliases={'摸摸'}, priority=26)


@petpet.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qq = event.user_id
    msg = event.get_message()
    for msg_seg in msg:
        if msg_seg.type == 'at':
            qq = msg_seg.data['qq']
            break
    file_path = await get_petpet(qq)
    if file_path:
        await petpet.send(message=MessageSegment.image(file='file://' + file_path))
        await petpet.finish()
    else:
        await petpet.finish('出错了，请稍后再试')
