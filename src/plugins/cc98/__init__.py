import re
from typing import Type, List, Union
from nonebot.rule import to_me
from nonebot import on_regex, on_command
from nonebot.matcher import Matcher
from nonebot.typing import T_Handler, T_State
from nonebot.adapters.cqhttp import Bot, Event, Message, MessageSegment, unescape

from nonebot.log import logger

from .emoji import emoji_list, get_emoji
from .data_source import cc98_api


async def handle_emoji(matcher: Type[Matcher], event: Event, dir_name: str):
    file_name = unescape(event.get_plaintext()).strip().strip('[').strip(']')
    img = get_emoji(dir_name, file_name)
    if img:
        await matcher.send(MessageSegment.image(img))
    else:
        await matcher.send('找不到该表情')


def create_emoji_matchers():

    def create_handler(dir_name: str) -> T_Handler:
        async def handler(bot: Bot, event: Event, state: T_State):
            await handle_emoji(matcher, event, dir_name)
        return handler

    for _, params in emoji_list.items():
        matcher = on_regex(params['pattern'], priority=14)
        matcher.append_handler(create_handler(params['dir_name']))


create_emoji_matchers()


cc98 = on_command('cc98', aliases={'98', 'CC98'}, rule=to_me(), priority=13)
show = on_command('cc98看帖', aliases={'98看帖', 'CC98看帖'},
                  rule=to_me(), priority=13)


@cc98.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = event.get_plaintext().strip()
    if not keyword:
        await cc98.finish()
    state['keyword'] = keyword


@cc98.got('keyword')
async def _(bot: Bot, event: Event, state: T_State):
    keyword = state['keyword']
    try:
        board_name, score = cc98_api.get_board_name(keyword)
    except Exception as e:
        logger.warning(f"Error in get_board_name({keyword}): {e}")
        await cc98.finish('出错了，请稍后再试')

    if score >= 70:
        state['board_name'] = board_name
        state['confirm'] = 'y'
    else:
        state['board_name'] = board_name
        await cc98.send(f'你要看的是不是[{board_name}]?\n[y]是 [其他]结束')


@cc98.got('confirm')
async def _(bot: Bot, event: Event, state: T_State):
    if state['confirm'] not in ['y', 'Y', 'yes', 'Yes', '是']:
        await cc98.finish()
    board_name = state['board_name']
    try:
        topics = cc98_api.get_topics(board_name)
        msgs = cc98_api.print_topics(topics)
    except Exception as e:
        logger.warning(
            f"Error in get_topics or print_topics, board_name [{board_name}]: {e}")
        await cc98.finish('出错了，请稍后再试')

    await send_forward_msg(bot, event, msgs)


@show.handle()
async def _(bot: Bot, event: Event, state: T_State):
    keyword = event.get_plaintext().strip()
    if keyword and keyword.isdigit():
        state['topic_id'] = keyword
    else:
        await show.finish()


@show.got('topic_id')
async def _(bot: Bot, event: Event, state: T_State):
    topic_id = int(state['topic_id'])
    page = 1

    try:
        topic = cc98_api.topic(topic_id)
        posts = cc98_api.print_posts(state['topic'], page)
    except Exception as e:
        logger.warning(
            f"Error in topic or print_posts, topic_id: {topic_id}: {e}")
        await show.finish('出错了，请稍后再试')

    state['topic'] = topic
    state['page'] = page
    msgs = [await str_to_message(post) for post in posts]
    await send_forward_msg(bot, event, msgs)


@show.got('reply')
async def _(bot: Bot, event: Event, state: T_State):
    reply = state['reply']
    topic = state['topic']
    page = state['page']
    reply_num = topic["replyCount"] + 1

    if reply == '+':
        if reply_num - page * 10 <= 0:
            await show.reject('当前已是最后一页')
        page += 1
    elif reply == '-':
        if page == 1:
            await show.reject('当前已是第一页')
        page -= 1
    else:
        await show.reject()

    try:
        posts = cc98_api.print_posts(state['topic'], page)
    except Exception as e:
        logger.warning(
            f"Error in print_posts, topic_id: {topic['id']}, page: {page}: {e}")
        await show.finish('出错了，请稍后再试')

    state['page'] = page
    msgs = [await str_to_message(post) for post in posts]
    await send_forward_msg(bot, event, msgs)


async def str_to_message(text: str) -> Message:
    msgs_all = Message()
    msgs = await split_msg(text, r'(##emoji##.*?##/emoji##)',
                           r'##emoji##(.*?)##/emoji##', cc98_api.replace_emoji)
    for seg in msgs:
        if seg.type == 'text':
            msgs_new = await split_msg(text, r'(##img##.*?##/img##)',
                                       r'##img##(.*?)##/img##', cc98_api.replace_url)
            msgs_all.extend(msgs_new)
        else:
            msgs_all.append(seg)
    return msgs_all


async def split_msg(text: str, split_pattern: str, pattern: str, func) -> Message:
    texts = re.split(split_pattern, text)
    msgs = Message()
    for t in texts:
        match = re.match(pattern, t)
        if match:
            result = await func(match.group(1))
            if not result:
                continue
            if isinstance(result, str):
                msgs.append(result)
            else:
                msgs.append(MessageSegment.image(result))
        else:
            msgs.append(t)
    return msgs


async def send_forward_msg(bot: Bot, event: Event, msgs: List[Union[str, MessageSegment]]):
    if not msgs:
        return

    def to_json(msg):
        return {
            'type': 'node',
            'data': {
                'name': '匿名114514',
                'uin': bot.self_id,
                'content': msg
            }
        }
    msgs = [to_json(msg) for msg in msgs]
    await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)
