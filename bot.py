#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot


# Custom your logger
# 
from nonebot.log import logger, default_format
logger.add("nonebot.log",
           diagnose=False,
           level="DEBUG",
           format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

nonebot.load_builtin_plugins()
nonebot.load_plugins("src/plugins")
nonebot.load_plugin("nonebot_plugin_status")
nonebot.load_plugin("nonebot_plugin_apscheduler")

# Modify some config / config depends on loaded configs
# 
# config = driver.config
# do something...


if __name__ == "__main__":
    nonebot.run(app="bot:app")
