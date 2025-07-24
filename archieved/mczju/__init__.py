from nonebot import on_command, on_notice, require
from nonebot.matcher import Matcher
from nonebot.rule import Rule

require("nonebot_plugin_orm")
require("nonebot_plugin_saa")
require("nonebot_plugin_apscheduler")

from nonebot.adapters.onebot.v11 import Bot, Event, PokeNotifyEvent
from nonebot_plugin_saa import SaaTarget, enable_auto_select_bot

enable_auto_select_bot()

from . import pusher as pusher
from . import recorder as recorder
from .config import dynmap_targets
from .data_source import get_dynmap_status


def in_dynmap_targets(target: SaaTarget):
    return target.dict() in [t.dict() for t in dynmap_targets]


def poke_rule(bot: Bot, event: Event) -> bool:
    return isinstance(event, PokeNotifyEvent) and str(event.target_id) == bot.self_id


status = on_command("status", rule=in_dynmap_targets, priority=14, block=True)
poke_status = on_notice(Rule(poke_rule) & in_dynmap_targets, priority=15, block=False)


@status.handle()
@poke_status.handle()
async def _(matcher: Matcher):
    status = await get_dynmap_status()
    if not status:
        await matcher.finish("出错了，请稍后再试")
    await matcher.finish(status)
