from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot import on_command, require
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_htmlrender import md_to_pic
from nonebot_plugin_apscheduler import scheduler

from .data_source import chat_bot
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="ChatGPT",
    description="ChatGPT AI对话",
    usage="chat/chatgpt xxx\n对话是连续的\n发送“刷新对话” 可以重新开始对话",
    config=Config,
    extra={
        "example": "chat 你好",
    },
)

chatgpt = on_command("chat", aliases={"chatgpt"}, block=True, priority=15)


@chatgpt.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if not msg:
        matcher.stop_propagation()
        await matcher.finish()
    try:
        reply = await chat_bot.get_reply(msg, event.get_session_id())
    except:
        await matcher.finish("出错了，请稍后再试")

    if len(reply) > 150 or "```" in reply:
        if reply.count("```") % 2 != 0:
            reply += "\n```"
        img = await md_to_pic(reply, width=600)
        res = MessageSegment.image(img)
    else:
        res = reply

    await matcher.finish(res, reply_message=True)


refresh = on_command("刷新对话", aliases={"刷新会话"}, block=True, priority=15)


@refresh.handle()
async def _(event: MessageEvent):
    chat_bot.refresh_session(event.get_session_id())
    await refresh.send("当前会话已刷新")


@scheduler.scheduled_job("interval", minutes=30)
async def _():
    await chat_bot.refresh_token()
