import nonebot
from nonebot import scheduler

from .users import *


@scheduler.scheduled_job('cron', day='*', hour=6, minute=0, second=0, misfire_grace_time=3600)
async def auto_signin():
    await cc98_signin()


async def cc98_signin():
    bot = nonebot.get_bot()
    for user in users:
        if user.api.signin_status()['hasSignedInToday']:
            msg = 'CC98用户 ' + user.username + ' 当前已签到，自动签到取消'
        elif not user.api.signin(data="sign in!"):
            msg = 'CC98用户 ' + user.username + ' 签到失败，请手动签到'
        else:
            msg = 'CC98用户 ' + user.username + ' 签到成功，'
            signin_data = user.api.get_signin_data()
            if signin_data is None:
                msg += '获取签到信息失败，请手动查看'
            else:
                msg += '您已连续签到 ' + signin_data[2] + ' 天，本次签到获得 ' + signin_data[3] + ' 财富值'
        try:
            await bot.send_private_msg(user_id=user.qq, message=msg)
        except:
            continue
