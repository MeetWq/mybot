from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, Message

from .data_source import get_tarot

draw = on_command('draw', priority=36)


@draw.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = event.get_plaintext().strip().split()[0]
    func = get_func(msg)
    if not func:
        return
    username = event.sender.card or event.sender.nickname
    message = Message(f'来看看 {username} 抽到了什么：')
    reponse = await func()
    message.extend(reponse)
    await draw.finish(message)


def get_func(msg: str):
    maps = [
        {
            'keywords': ['塔罗牌', 'tarot'],
            'function': get_tarot
        }
    ]
    for map in maps:
        for keyword in map['keywords']:
            if keyword in msg:
                return map['function']
    return None
