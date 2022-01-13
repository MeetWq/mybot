import re
from typing import List, Union
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, ArgPlainText, State
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment

from .data_source import CaiyunAi, model_list


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
                   block=True, rule=to_me(), priority=11)


@novel.handle()
async def first_receive(matcher: Matcher, msg: Message = CommandArg()):
    content = msg.extract_plain_text().strip()
    if content:
        matcher.set_arg('content', msg)


@novel.got('content', prompt='请发送要续写的内容')
async def _(bot: Bot, event: GroupMessageEvent,
            state: T_State = State(), content: str = ArgPlainText()):
    caiyunai = CaiyunAi()
    state['caiyunai'] = caiyunai

    content = content.strip()
    if not content:
        await novel.reject()
    await novel.send('loading...')
    caiyunai.content = content
    await caiyunai.get_contents()
    if caiyunai.err_msg:
        await novel.finish(f"出错了：{caiyunai.err_msg}")
    else:
        await send_contents(bot, event, caiyunai)


@novel.got('input')
async def _(bot: Bot, event: GroupMessageEvent,
            state: T_State = State(), input: str = ArgPlainText()):
    caiyunai: CaiyunAi = state.get('caiyunai')
    input = input.strip()
    match_continue = re.fullmatch(r'续写\s*(\d+)', input)
    match_model = re.fullmatch(r'切换模型(.*?)', input)
    match_finish = re.match(r'结束', input)

    if match_continue:
        num = int(match_continue.group(1))
        if 1 <= num <= len(caiyunai.contents):
            caiyunai.nodeid = caiyunai.nodeids[num-1]
            caiyunai.content = caiyunai.contents[num-1]
            await novel.send('loading...')
            await caiyunai.get_contents()
            if caiyunai.err_msg:
                await novel.finish(f"出错了：{caiyunai.err_msg}")
            else:
                await send_contents(bot, event, caiyunai)
        else:
            await novel.send('请发送正确的编号')
    elif match_model:
        model = match_model.group(1).strip()
        if model not in model_list:
            model_help = f"支持的模型：{'、'.join(list(model_list))}\n发送“切换模型 名称”切换模型"
            await novel.send(model_help)
        else:
            caiyunai.model = model
            await novel.send(f'模型已切换为：{model}')
    elif match_finish:
        await novel.finish('当前会话已结束')

    await novel.reject()


async def send_contents(bot: Bot, event: GroupMessageEvent, caiyunai: CaiyunAi):
    msgs = []
    nickname = model_list[caiyunai.model]['name']
    help_msg = '发送“续写 编号”选择续写分支\n发送“切换模型 名称”切换模型\n发送“结束”结束会话'
    msgs.append(help_msg)
    msgs.append(caiyunai.result)
    for i, content in enumerate(caiyunai.contents, start=1):
        msgs.append(f'{i}、\n{content}')
    await send_forward_msg(bot, event, nickname, bot.self_id, msgs)


async def send_forward_msg(bot: Bot, event: GroupMessageEvent, name: str, uin: str,
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
