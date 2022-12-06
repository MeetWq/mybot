from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot import get_driver, on_command, require
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_htmlrender import md_to_pic
from nonebot_plugin_apscheduler import scheduler

from .data_source import chat_bot
from .config import Config

chat_config = Config.parse_obj(get_driver().config.dict())

__plugin_meta__ = PluginMetadata(
    name="ChatGPT",
    description="ChatGPT AI对话",
    usage="chat xxx",
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

    if len(reply) > 300:
        img = await md_to_pic(reply, width=800)
        res = MessageSegment.image(img)
    else:
        res = reply

    await matcher.finish(res, reply_message=True)


@scheduler.scheduled_job("interval", minutes=30)
async def refresh_session() -> None:
    await chat_bot.refresh_token()
