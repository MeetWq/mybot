import re
import math
import traceback
from typing import List, Union, Type
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot import on_regex, on_command
from nonebot.typing import T_Handler, T_State
from nonebot.params import CommandArg, ArgPlainText, EventPlainText, State
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.log import logger

from .emoji import emoji_list, get_emoji
from .data_source import (
    cc98_api,
    get_board_name,
    get_topics,
    replace_emoji,
    replace_url,
    print_topics,
    print_posts,
)


async def handle_emoji(matcher: Type[Matcher], dirname: str, filename: str):
    img = get_emoji(dirname, filename)
    if img:
        await matcher.send(MessageSegment.image(img))
    else:
        await matcher.send("找不到该表情")


def create_emoji_matchers():
    def create_handler(dirname: str) -> T_Handler:
        async def handler(filename: str = EventPlainText()):
            filename = filename.strip().strip("[").strip("]")
            await handle_emoji(matcher, dirname, filename)

        return handler

    for _, params in emoji_list.items():
        matcher = on_regex(params["pattern"], block=True, priority=14)
        matcher.append_handler(create_handler(params["dirname"]))


create_emoji_matchers()


cc98 = on_command("cc98", aliases={"98", "CC98"}, block=True, rule=to_me(), priority=13)
show = on_command(
    "cc98看帖", aliases={"98看帖", "CC98看帖"}, block=True, rule=to_me(), priority=13
)


@cc98.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if not keyword:
        await cc98.finish()
    matcher.set_arg("keyword", Message(keyword))


@cc98.got("keyword")
async def _(matcher: Matcher, keyword: str = ArgPlainText(), state: T_State = State()):
    try:
        res = await get_board_name(keyword)
    except:
        logger.warning(traceback.format_exc())
        await cc98.finish("出错了，请稍后再试")

    if res:
        board_name, score = res
        state["board_name"] = board_name
        if score >= 70:
            matcher.set_arg("confirm", Message("y"))
        else:
            await cc98.send(f"你要看的是不是[{board_name}]?\n[y]是 [其他]结束")


@cc98.got("confirm")
async def _(
    bot: Bot,
    event: GroupMessageEvent,
    state: T_State = State(),
    confirm: str = ArgPlainText(),
):
    board_name: str = state.get("board_name", "")
    if confirm not in ["y", "Y", "yes", "Yes", "是"]:
        await cc98.finish()
    try:
        topics = await get_topics(board_name)
        msgs = await print_topics(topics)
    except:
        logger.warning(traceback.format_exc())
        await cc98.finish("出错了，请稍后再试")

    await send_forward_msg(bot, event, msgs)


@show.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    keyword = msg.extract_plain_text().strip()
    if keyword and keyword.isdigit():
        matcher.set_arg("topic_id", Message(keyword))
    else:
        await show.finish()


@show.got("topic_id")
async def _(
    bot: Bot,
    event: GroupMessageEvent,
    state: T_State = State(),
    topic_id: str = ArgPlainText(),
):
    page = 1
    try:
        topic = await cc98_api.topic(topic_id)
        posts = await print_posts(topic, page)
    except:
        logger.warning(traceback.format_exc())
        await show.finish("出错了，请稍后再试")

    state["topic"] = topic
    state["page"] = page
    msgs = [await str_to_message(post) for post in posts]
    await send_forward_msg(bot, event, msgs)


@show.got("reply")
async def _(
    bot: Bot,
    event: GroupMessageEvent,
    state: T_State = State(),
    reply: str = ArgPlainText(),
):
    topic: dict = state.get("topic", {})
    page: int = state.get("page", 1)
    reply_num = topic["replyCount"] + 1

    if reply == "结束":
        await show.finish("会话已结束")
    elif reply == "+":
        if reply_num - page * 10 <= 0:
            await show.reject("当前已是最后一页")
        page += 1
    elif reply == "-":
        if page == 1:
            await show.reject("当前已是第一页")
        page -= 1
    elif reply.isdigit():
        if not (1 <= int(reply) <= math.ceil(reply_num / 10)):
            await show.reject("请输入正确的页码")
        page = int(reply)
    else:
        await show.reject()

    try:
        posts = await print_posts(topic, page)
    except:
        logger.warning(traceback.format_exc())
        await show.finish("出错了，请稍后再试")

    state["page"] = page
    msgs = [await str_to_message(post) for post in posts]
    await send_forward_msg(bot, event, msgs)
    await show.reject()


async def str_to_message(text: str) -> Message:
    msgs_all = Message()
    msgs = await split_msg(
        text, r"(##emoji##.*?##/emoji##)", r"##emoji##(.*?)##/emoji##", replace_emoji
    )
    for seg in msgs:
        if seg.type == "text":
            msgs_new = await split_msg(
                seg.data["text"],
                r"(##img##.*?##/img##)",
                r"##img##(.*?)##/img##",
                replace_url,
            )
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
            msgs.append(result)
        else:
            msgs.append(t)
    return msgs


async def send_forward_msg(
    bot: Bot,
    event: GroupMessageEvent,
    msgs: Union[List[str], List[MessageSegment], List[Message]],
):
    if not msgs:
        return

    def to_json(msg):
        return {
            "type": "node",
            "data": {"name": "匿名114514", "uin": bot.self_id, "content": msg},
        }

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )
