from pathlib import Path
from nonebot import on_notice
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
    Bot,
    GroupIncreaseNoticeEvent,
)

dir_path = Path(__file__).parent
welcome_path = dir_path / "resources" / "welcome.jpg"


async def welcome_rule(bot: Bot, event: GroupIncreaseNoticeEvent) -> bool:
    return event.user_id != bot.self_id


welcome = on_notice(rule=Rule(welcome_rule), priority=10)


@welcome.handle()
async def _(event: GroupIncreaseNoticeEvent):
    if str(event.group_id) == "196608911":
        await welcome.finish(
            Message.template("欢迎 {user_id:at} 来到浙大MC，啪啪啪啪啪！").format(
                user_id=event.user_id
            )
        )
    await welcome.finish(MessageSegment.image(welcome_path.read_bytes()))
