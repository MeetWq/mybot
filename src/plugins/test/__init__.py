from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

test = on_command("test", rule=to_me(), block=True, permission=SUPERUSER, priority=10)


@test.handle()
async def _():
    await test.send(message="hello")
