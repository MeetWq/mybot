import os
import json
from nonebot import on_command, CommandSession, permission
from nonebot.message import unescape


@on_command('send_msg', aliases=('发送', 'send'), permission=permission.SUPERUSER)
async def send_msg(session: CommandSession):
    path = os.path.join('my', 'plugins', 'send_msg', 'friend_list.json')
    with open(path, "r") as f:
        friends = json.load(f)
    bot = session.bot
    groups = await bot.get_group_list()
    n = 1
    send_list = '发送列表：\n'
    for friend in friends:
        send_list += '[' + str(n) + ']' + friend['nickname'] + '\n'
        n += 1
    for group in groups:
        send_list += '[' + str(n) + ']' + group['group_name'] + '(群)\n'
        n += 1
    send_list += '输入编号进行发送'

    while True:
        num = session.get('num', prompt=send_list)
        if num.isdigit():
            num = int(num)
            if len(friends) + len(groups) >= num >= 1:
                break
            else:
                session.state.pop('num')
                await session.send('请输入正确的编号')
        else:
            session.finish('会话结束')

    if num <= len(friends):
        message_type = 'private'
        send_id = friends[num - 1]['user_id']
        send_name = friends[num - 1]['nickname']
    else:
        message_type = 'group'
        send_id = groups[num - len(friends) - 1]['group_id']
        send_name = groups[num - len(friends) - 1]['group_name'] + '(群)'

    answer = session.get('answer', prompt='确认要发送信息给 ' + send_name + ' ?\n' +
                                          '[y]是 [其他]结束')
    if answer in ['y', 'Y', 'yes', 'Yes', '是']:
        if 'start' not in session.state.keys():
            session.state['start'] = True
            await session.send('会话开始')
        while True:
            content = session.get('content')
            session.state.pop('content')
            if message_type == 'private':
                await bot.send_private_msg(user_id=send_id, message=unescape(content))
            elif message_type == 'group':
                await bot.send_group_msg(group_id=send_id, message=unescape(content))
    else:
        session.finish('会话结束')


@send_msg.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['num'] = stripped_arg
        return

    if not stripped_arg:
        session.finish('会话结束')

    session.state[session.current_key] = stripped_arg
