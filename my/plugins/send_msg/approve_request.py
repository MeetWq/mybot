import os
import json
from nonebot import on_request, RequestSession
from config import my_qq


@on_request('friend')
async def _(session: RequestSession):
    await session.approve()

    bot = session.bot
    user_id = session.ctx['user_id']
    nickname = bot.get_stranger_info(user_id=user_id)['nickname']

    path = os.path.join('my', 'plugins', 'send_msg', 'friend_list.json')
    with open(path, "r") as f:
        friends = json.load(f)
    new_friend = {'user_id': user_id, 'nickname': nickname}
    friends.append(new_friend)
    with open(path, "w") as f:
        json.dump(friends, f)

    msg = '用户' + user_id + '请求加为好友\n' + \
          '验证信息：' + session.ctx['comment']
    await bot.send_private_msg(user_id=my_qq, message=msg)


@on_request('group')
async def _(session: RequestSession):
    if session.ctx['sub_type'] == 'invite':
        await session.approve()
        msg = '用户' + session.ctx['user_id'] + \
              '邀请你加入群聊' + session.ctx['group_id']
        bot = session.bot
        await bot.send_private_msg(user_id=my_qq, message=msg)
