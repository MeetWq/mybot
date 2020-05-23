from nonebot import on_command, CommandSession, permission


@on_command('test', aliases=('测试', 'hello'), permission=permission.SUPERUSER)
async def test_command(session: CommandSession):
    await session.send('hello')
