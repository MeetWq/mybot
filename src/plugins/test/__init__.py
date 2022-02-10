from nonebot import on_command
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER

test = on_command("test", rule=to_me(), block=True, permission=SUPERUSER, priority=10)


@test.handle()
async def _():
    await test.send(message="hello")
