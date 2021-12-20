import re
from typing import List, Union
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.log import logger

from .data_source import get_contents, model_list, ContentError


__des__ = '彩云小梦自动续写'
__cmd__ = '''
@我 续写/彩云小梦 {text}
'''.strip()
__short_cmd__ = '@我 续写 xxx'
__example__ = '''
@小Q 续写 小Q是什么
'''.strip()
__usage__ = f'{__des__}\nUsage:\n{__cmd__}\nExample:\n{__example__}'


novel = on_command('caiyunai', aliases={'续写', '彩云小梦'},
                   rule=to_me(), priority=11)


def handle_exception(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.warning(str(e))
            if isinstance(e, ContentError):
                await novel.reject('存在不和谐内容，请重新发送')
            else:
                await novel.reject('出错了，请稍后再试')
    return wrapper


get_contents = handle_exception(get_contents)


@novel.handle()
async def first_receive(bot: Bot, event: Event, state: T_State):
    content = event.get_plaintext().strip()
    if content:
        state['content'] = content


@novel.got('content', prompt='请发送要续写的内容')
async def _(bot: Bot, event: Event, state: T_State):
    await novel.send('loading...')
    await get_contents(state, first=True)
    await send_contents(bot, event, state)


@novel.got('input')
async def _(bot: Bot, event: Event, state: T_State):
    input = state['input']
    match_continue = re.fullmatch(r'续写\s*(\d+)', input)
    match_model = re.fullmatch(r'切换模型(.*?)', input)
    match_finish = re.search(r'结束', input)

    if match_continue:
        num = int(match_continue.group(1))
        if 1 <= num <= len(state['contents']):
            state['nodeid'] = state['nodeids'][num - 1]
            state['content'] = state['contents'][num - 1]
            await novel.send('loading...')
            await get_contents(state)
            await send_contents(bot, event, state)
        else:
            await novel.send('请发送正确的编号')
    elif match_model:
        model = match_model.group(1).strip()
        if model not in model_list:
            model_help = f"支持的模型：{'、'.join(list(model_list))}\n发送“切换模型 名称”切换模型"
            await novel.send(model_help)
        else:
            state['model'] = model
            await novel.send(f'模型已切换为：{model}')
    elif match_finish:
        await novel.finish('当前会话已结束')

    await novel.reject()


async def send_contents(bot: Bot, event: Event, state: T_State):
    msgs = []
    nickname = model_list[state['model']]['name']
    help_msg = '发送“续写 编号”选择续写分支\n发送“切换模型 名称”切换模型\n发送“结束”结束会话'
    msgs.append(help_msg)
    msgs.append(state['result'])
    for i, content in enumerate(state['contents'], start=1):
        msgs.append(f'{i}、\n{content}')
    await send_forward_msg(bot, event, nickname, bot.self_id, msgs)


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
