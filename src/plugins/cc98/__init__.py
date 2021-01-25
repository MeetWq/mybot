import re
import traceback
from nonebot import on_command, on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, Message
from nonebot.log import logger

from .user import cc98_api
from .data_source import CC98Error
from .word_filter import DFAFilter

cc98_pattern = r'^([cC]{2})?98(.*)'
cc98 = on_regex(cc98_pattern, rule=to_me(), priority=13)
show = on_command('看帖', aliases={'打开帖子', '快速看帖'}, rule=to_me(), priority=14)

dfa_filter = DFAFilter()


@cc98.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    key_word = re.match(cc98_pattern, msg).group(2)
    if key_word:
        state['key_word'] = key_word


@cc98.got('key_word', prompt='请输入关键词（如：十大，新帖，心灵）查看帖子列表')
async def _(bot: Bot, event: Event, state: T_State):
    try:
        board_name, score = cc98_api.get_board_name(state['key_word'])
        if score >= 70:
            state['board_name_get'] = board_name
            state['confirm'] = 'y'
        else:
            state['board_name_get'] = board_name
            await cc98.send(message='你要看的是不是[{}]?\n[y]是 [其他]结束'.format(board_name))
    except CC98Error:
        logger.warning("Error in cc98: {}".format(traceback.format_exc()))
        await cc98.finish('出现错误，请稍后重试')


@cc98.got('confirm')
async def _(bot: Bot, event: Event, state: T_State):
    try:
        if state['confirm'] in ['y', 'Y', 'yes', 'Yes', '是']:
            state['board_name'] = state['board_name_get']
        else:
            await cc98.finish('会话结束')
        state['topics'] = cc98_api.get_topics(state['board_name'])
        msg = cc98_api.print_topics(state['topics'])
        msg = dfa_filter.word_replace(msg)
        await cc98.send(message=msg)
    except CC98Error:
        logger.warning("Error in cc98: {}".format(traceback.format_exc()))
        await cc98.finish('出现错误，请稍后重试')


@cc98.got('reply')
async def show_post(bot: Bot, event: Event, state: T_State):
    try:
        topics = state['topics']
        reply = state['reply']
        if reply.isdigit():
            num = int(reply)
            if len(topics) >= num >= 1:
                state['num'] = num
                state['page'] = 1
                topic = topics[num - 1]
                await cc98.send(message="加载中，请稍候...")
                await cc98.send(message=Message(str_to_message(cc98_api.print_posts(topic, 1))))
                await cc98.reject()
            else:
                await cc98.reject('请输入正确的编号')
        elif reply == '+' or reply == '-':
            if 'num' not in state.keys():
                await cc98.reject()
            num = state['num']
            page = state['page']
            topic = topics[num - 1]
            reply_num = topic["replyCount"] + 1
            if page == 1 and reply == '-':
                await cc98.reject('当前已是第一页')
            elif reply_num - page * 10 <= 0 and reply == '+':
                await cc98.reject('当前已是最后一页')
            else:
                if reply == '+':
                    page += 1
                elif reply == '-':
                    page -= 1
                state['page'] = page
                await cc98.send(message="加载中，请稍候...")
                await cc98.send(message=Message(str_to_message(cc98_api.print_posts(topic, page))))
                await cc98.reject()
        else:
            await cc98.finish('会话结束')
    except CC98Error:
        logger.warning("Error in cc98: {}".format(traceback.format_exc()))
        await cc98.finish('出现错误，请稍后重试')


def str_to_message(text: str):
    if len(text) > 2000:
        return [{"type": "text", "data": {"text": "帖子内容过长，请移步98查看"}}]
    split_pattern = r'(##file##.*?##/file##)'
    img_pattern = r'##file##(.*?)##/file##'
    texts = re.split(split_pattern, text)
    msgs = []
    for t in texts:
        match = re.match(img_pattern, t)
        if match:
            msgs.append({"type": "image", "data": {"file": "file://" + match.group(1)}})
        else:
            msgs.append({"type": "text", "data": {"text": dfa_filter.word_replace(t)}})
    return msgs


@show.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message()).strip()
    if msg and msg.isdigit():
        state['topic_id'] = msg


@show.got('topic_id', prompt='请输入帖子id')
async def _(bot: Bot, event: Event, state: T_State):
    try:
        state['topic'] = cc98_api.topic(int(state['topic_id']))
        state['page'] = 1
        await cc98.send(message="加载中，请稍候...")
        await cc98.send(message=Message(str_to_message(cc98_api.print_posts(state['topic'], 1))))
    except CC98Error:
        logger.warning("Error in cc98: {}".format(traceback.format_exc()))
        await cc98.finish('出现错误，请稍后重试')


@show.got('reply')
async def _(bot: Bot, event: Event, state: T_State):
    try:
        reply = state['reply']
        if reply == '+' or reply == '-':
            topic = state['topic']
            page = state['page']
            reply_num = topic["replyCount"] + 1
            if page == 1 and reply == '-':
                await cc98.reject('当前已是第一页')
            elif reply_num - page * 10 <= 0 and reply == '+':
                await cc98.reject('当前已是最后一页')
            else:
                if reply == '+':
                    page += 1
                elif reply == '-':
                    page -= 1
                state['page'] = page
                await cc98.send(message="加载中，请稍候...")
                await cc98.send(message=Message(str_to_message(cc98_api.print_posts(topic, page))))
                await cc98.reject()
        else:
            await cc98.finish('会话结束')
    except CC98Error:
        logger.warning("Error in cc98: {}".format(traceback.format_exc()))
        await cc98.finish('出现错误，请稍后重试')
