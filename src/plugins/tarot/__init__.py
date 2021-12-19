from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, Message, MessageSegment

from .data_source import get_tarot


__des__ = '塔罗牌占卜'
__cmd__ = '''
单张塔罗牌
'''.strip()
__short_cmd__ = __cmd__
__notice__ = '''
生成的图片为幻影坦克图，手机端或黑色背景下才能显示
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nNotice:\n{__notice__}'


tarot = on_command('tarot', aliases={'单张塔罗牌', '塔罗牌占卜'}, priority=36)


@tarot.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = event.sender.card or event.sender.nickname
    message = Message(f'来看看 {username} 抽到了什么：')
    img = await get_tarot()
    if img:
        message.append(MessageSegment.image(img))
        await tarot.finish(message)
    else:
        await tarot.finish('出错了，请稍后再试')
