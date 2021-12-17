import re
import random
from typing import List, Union
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.log import logger

from .life import Life
from .talent import Talent


__des__ = '人生重开模拟器'
__cmd__ = '''
@我 remake/liferestart/人生重开
'''.strip()
__short_cmd__ = __cmd__
__example__ = '''
@小Q remake
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


remake = on_command('remake', aliases={'liferestart', '人生重开'},
                    rule=to_me(), priority=28)


@remake.handle()
async def first_receive(bot: Bot, event: Event, state: T_State):
    life = Life()
    talents = life.rand_talents(10)
    state['life'] = life
    state['talents'] = talents
    msg = '请发送编号选择3个天赋，如“0 1 2”，或发送“随机”随机选择；发送“结束”结束会话'
    des = [f'{i}.{t.name}（{t.description}）' for i, t in enumerate(talents)]
    des = '\n'.join(des)
    await remake.send(f"{msg}\n\n{des}")


@remake.got('nums')
async def _(bot: Bot, event: Event, state: T_State):
    reply = state['nums']
    match = re.fullmatch(r'\s*(\d)\s*(\d)\s*(\d)\s*', reply)
    if match:
        nums = list(match.groups())
        nums = [int(n) for n in nums]
        nums.sort()
    elif reply == '随机':
        nums = random.sample(range(10), 3)
        nums.sort()
    elif reply == '结束':
        await remake.finish()
    else:
        await remake.reject()

    talents: List[Talent] = state['talents']
    state['talents_selected'] = [talents[n] for n in nums]
    msg = '请发送4个数字分配“颜值、智力、体质、家境”4个属性，如“5 5 5 5”，属性之和需为20，每个属性不能超过10；或发送“随机”随机选择；发送“结束”结束会话'
    await remake.send(msg)


@remake.got('prop')
async def _(bot: Bot, event: Event, state: T_State):
    reply = state['prop']
    match = re.fullmatch(
        r'\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s*', reply)
    if match:
        nums = list(match.groups())
        nums = [int(n) for n in nums]
        if sum(nums) != 20:
            await remake.reject('属性之和需为20，请重新输入')
        elif max(nums) > 10:
            await remake.reject('属性不能超过10，请重新输入')
    elif reply == '随机':
        num1 = random.randint(0, 10)
        num2 = random.randint(0, 10)
        nums = [num1, num2, 10-num1, 10-num2]
        random.shuffle(nums)
    elif reply == '结束':
        await remake.finish()
    else:
        await remake.reject()

    life: Life = state['life']
    talents: List[Talent] = state['talents_selected']
    prop = {'CHR': nums[0], 'INT': nums[1], 'STR': nums[2], 'MNY': nums[3]}
    life.set_talents(talents)
    life.apply_property(prop)

    await remake.send('你的人生正在重开...')

    msgs = []
    talent_msg = '已选择以下天赋：'
    talent_des = [f'{t.name}（{t.description}）' for t in talents]
    talent_des = '\n'.join(talent_des)
    msgs.append(f'{talent_msg}\n{talent_des}')
    prop_des = f'已设置如下属性：\n颜值{nums[0]} 智力{nums[1]} 体质{nums[2]} 家境{nums[3]}'
    msgs.append(prop_des)
    try:
        for s in life.run():
            msgs.append('\n'.join(s))
        msgs.append(life.gen_summary())
    except Exception as e:
        logger.warning(f'Error in remake: {e}')
        await remake.finish('出错了，请稍后再试')

    await send_forward_msg(bot, event, '人生重开模拟器', bot.self_id, msgs)
    await remake.finish()


async def send_forward_msg(bot: Bot, event: Event, name: str, uin: str,
                           msgs: List[Union[str, MessageSegment]]):
    if not msgs:
        return

    def to_json(msg):
        return {
            'type': 'node',
            'data': {
                'name': name,
                'uin': uin,
                'content': msg
            }
        }
    msgs = [to_json(msg) for msg in msgs]
    await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)
