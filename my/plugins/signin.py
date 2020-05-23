from nonebot import on_command, permission

from my.plugins.cc98.auto_signin import cc98_signin
from my.plugins.nhd.auto_signin import nhd_signin


@on_command('signin', aliases=('签到', '手动签到'), permission=permission.SUPERUSER)
async def signin():
    await cc98_signin()
    await nhd_signin()
