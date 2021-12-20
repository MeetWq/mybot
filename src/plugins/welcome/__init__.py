from pathlib import Path
from nonebot import on_notice
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, GroupIncreaseNoticeEvent

dir_path = Path(__file__).parent
welcome_path = dir_path / 'resources' / 'welcome.jpg'


async def welcome_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupIncreaseNoticeEvent) and event.user_id != bot.self_id


welcome = on_notice(rule=welcome_rule, priority=10)


@welcome.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await welcome.finish(MessageSegment.image(welcome_path.read_bytes()))
