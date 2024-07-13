from nonebot import on_command, require
from nonebot.matcher import Matcher

require("nonebot_plugin_orm")
require("nonebot_plugin_saa")
require("nonebot_plugin_apscheduler")

from nonebot_plugin_saa import SaaTarget, enable_auto_select_bot

enable_auto_select_bot()

from . import pusher as pusher
from . import recorder as recorder
from .config import dynmap_targets
from .data_source import get_dynmap_status


async def in_dynmap_targets(target: SaaTarget):
    return target.dict() in [t.dict() for t in dynmap_targets]


status = on_command("status", rule=in_dynmap_targets, priority=14, block=True)


@status.handle()
async def _(matcher: Matcher):
    status = await get_dynmap_status()
    if not status:
        await matcher.finish("出错了，请稍后再试")
    await matcher.finish(status)
