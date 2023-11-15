from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_saa")
require("nonebot_plugin_htmlrender")

from nonebot_plugin_saa import Image, MessageFactory

from .data_source import get_crafatar, get_mc_uuid, get_mcmodel, get_mcstatus

__plugin_meta__ = PluginMetadata(
    name="Minecraft",
    description="Minecraft相关功能",
    usage=(
        "1、mcstatus {url}，MC服务器状态查询\n"
        "2、mc avatar/head/body/skin/cape/model {id}，获取MC用户的 头像/头/身体/皮肤/披风/全身动图\n"
    ),
    extra={
        "example": "mcstatus mczju.tpddns.cn\nmcskin hsds",
    },
)


mc = on_command("mc", block=True, priority=12)


@mc.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    if not msg:
        await matcher.finish()
    if msg.startswith("status"):
        addr = msg.replace("status", "", 1).strip()
        if addr:
            result = await get_mcstatus(addr)
            if result:
                icon, status = result
                message = MessageFactory([])
                if icon:
                    message.append(Image(icon))
                message.append(status)
                await message.send()
            else:
                await matcher.finish("出错了，请稍后再试")
    else:
        types = ["avatar", "head", "body", "skin", "cape", "model"]
        for t in types:
            if msg.startswith(t):
                username = msg.replace(t, "", 1).strip()
                if username:
                    uuid = await get_mc_uuid(username)
                    if not uuid:
                        await matcher.finish("出错了，请稍后再试")
                    if uuid == "none":
                        await matcher.finish("找不到该用户")
                    if t == "model":
                        await matcher.send("生成中，请耐心等待。。。")
                        result = await get_mcmodel(uuid)
                    else:
                        result = await get_crafatar(t, uuid)
                    if result:
                        await MessageFactory([Image(result)]).send()
                    else:
                        await matcher.finish("出错了，请稍后再试")
    await matcher.finish()
