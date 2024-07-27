from nonebot import on_command, on_notice, require
from nonebot.matcher import Matcher
from nonebot.rule import to_me

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
poke_status = on_notice(to_me() & in_dynmap_targets, priority=15, block=False)


@status.handle()
@poke_status.handle()
async def _(matcher: Matcher):
    status = await get_dynmap_status()
    if not status:
        await matcher.finish("出错了，请稍后再试")
    await matcher.finish(status)
