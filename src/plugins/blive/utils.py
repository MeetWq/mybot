import re
from nonebot import get_bots


def user_type(user_id: str):
    p_group = r'group_(\d+)'
    p_private = r'private_(\d+)'
    match = re.fullmatch(p_group, user_id)
    if match:
        return 'group', match.group(1)
    match = re.fullmatch(p_private, user_id)
    if match:
        return 'private', match.group(1)
    return '', user_id


async def send_bot_msg(user_id, msg):
    type, id = user_type(user_id)
    bots = list(get_bots().values())
    for bot in bots:
        if type == 'group':
            await bot.send_group_msg(group_id=id, message=msg)
        elif type == 'private':
            await bot.send_private_msg(user_id=id, message=msg)
