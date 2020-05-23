import nonebot
from nonebot import scheduler

from .users import *


@scheduler.scheduled_job('cron', day='*', hour=6, minute=0, second=30, misfire_grace_time=3600)
async def auto_signin():
    await nhd_signin()


async def nhd_signin():
    bot = nonebot.get_bot()
    for user in users:
        if not user.login():
            msg = 'NHD用户 ' + user.username + ' 登录失败，请手动签到'
        elif user.signin_status():
            msg = 'NHD用户 ' + user.username + ' 当前已签到，自动签到取消'
        else:
            signin_data = user.signin()
            if not signin_data:
                msg = 'NHD用户 ' + user.username + ' 签到失败，请手动签到'
            else:
                msg = 'NHD用户 ' + user.username + ' 签到成功，'
                msg += '您已连续签到 ' + signin_data[0] + ' 天，本次签到获得 ' + signin_data[1] + ' 魔力值'
        try:
            await bot.send_private_msg(user_id=user.qq, message=msg)
        except:
            continue
