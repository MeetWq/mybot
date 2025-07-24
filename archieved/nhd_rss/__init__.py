from nonebot import require

require("nonebot_plugin_saa")
require("nonebot_plugin_htmlrender")
require("nonebot_plugin_apscheduler")

from nonebot_plugin_saa import enable_auto_select_bot

enable_auto_select_bot()

from . import pusher as pusher
