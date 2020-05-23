from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger

from .users import *
from .auto_signin import *
from .notice import *
from .my_cc98api import CC98Error

__plugin_name__ = 'CC98快速看帖'


@on_command('cc98', aliases=('98', 'CC98'))
async def cc98(session: CommandSession):
    if 'key_word' not in session.state.keys() or not session.state['key_word']:
        await session.send('目前可以查看cc98十大、新帖以及各版面的帖子，请输入 98 + 关键词 查看帖子')
        session.finish()
        return
    else:
        key_word = session.state.get('key_word')
    try:
        while 'topics' not in session.state.keys():
            board_name, topics, score = default_user.api.get_topics(key_word)
            if score > 50:
                session.state['topics'] = topics
                msgs = default_user.api.print_topics(topics)
                for msg in msgs:
                    await session.send(msg)
            else:
                answer = session.get('answer', prompt='你要看的是不是[' + board_name + ']?\n' +
                                                      '[y]是 [n]结束 [其他]重新输入')
                if answer in ['y', 'Y', 'yes', 'Yes', '是']:
                    session.state['topics'] = topics
                    msgs = default_user.api.print_topics(topics)
                    for msg in msgs:
                        await session.send(msg)
                elif answer in ['n', 'N', 'no', 'No', '否']:
                    session.finish('会话结束')
                else:
                    session.switch(answer)
        await show_topic(session)
    except CC98Error:
        await session.send('出现错误，请稍后重试')
        session.finish()


@on_command('看帖', aliases=('打开帖子', '快速看帖'))
async def show_posts(session: CommandSession):
    if 'topic_id' not in session.state.keys() or not session.state['topic_id']:
        await session.send('请输入 看帖 + id 查看帖子')
        session.finish()
        return
    try:
        while 'topic' not in session.state.keys():
            topic_id = session.state.get('topic_id')
            if topic_id.isdigit():
                topic_id = int(topic_id)
                topic = default_user.api.topic(topic_id)
                msgs = default_user.api.print_posts(topic, 1)
                session.state['topic'] = topic
                session.state['page'] = 1
                for msg in msgs:
                    await session.send(msg)
            else:
                session.state.pop('topic_id')
                await session.send('请输入正确的编号')
        await show_topic(session)
    except CC98Error:
        await session.send('出现错误，请稍后重试')
        session.finish()


async def show_topic(session: CommandSession):
    topics = session.state['topics']
    while True:
        reply = session.get('reply')
        session.state.pop('reply')
        if reply.isdigit():
            num = int(reply)
            if len(topics) >= num >= 1:
                session.state['num'] = num
                session.state['page'] = 1
                topic = topics[num - 1]
                msgs = default_user.api.print_posts(topic, 1)
                for msg in msgs:
                    await session.send(msg)
            else:
                await session.send('请输入正确的编号')
        elif reply == '+' or reply == '-':
            if 'num' not in session.state.keys():
                continue
            num = session.state['num']
            page = session.state['page']
            topic = topics[num - 1]
            reply_num = topic["replyCount"] + 1
            if page == 1 and reply == '-':
                await session.send('当前已是第一页')
            elif reply_num - page * 10 <= 0 and reply == '+':
                await session.send('当前已是最后一页')
            else:
                if reply == '+':
                    page += 1
                elif reply == '-':
                    page -= 1
                session.state['page'] = page
                msgs = default_user.api.print_posts(topic, page)
                for msg in msgs:
                    await session.send(msg)
        else:
            session.switch(session.ctx['message'])


@cc98.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['key_word'] = stripped_arg
        return

    if not stripped_arg:
        session.finish('会话结束')

    session.state[session.current_key] = stripped_arg


@show_posts.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['topic_id'] = stripped_arg
        return

    if not stripped_arg:
        session.finish('会话结束')

    session.state[session.current_key] = stripped_arg


@on_natural_language(keywords=('98', 'cc98', 'CC98'), only_to_me=False)
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    for words in ['98', 'cc98', 'CC98']:
        stripped_msg = stripped_msg.replace(words, '')
    return IntentCommand(90.0, 'cc98', current_arg=stripped_msg or '')


@on_natural_language(keywords=('看帖', '快速看帖'), only_to_me=False)
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    for words in ['看帖', '快速看帖']:
        stripped_msg = stripped_msg.replace(words, '')
    return IntentCommand(90.0, 'show_posts', current_arg=stripped_msg or '')
