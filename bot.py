#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from pathlib import Path
from typing import TYPE_CHECKING

from nonebot.adapters.onebot.v11 import Adapter as OneBot_V11_Adapter
from nonebot.log import logger, default_format

if TYPE_CHECKING:
    from loguru import Record

log_name = 'nonebot.log'
log_dir = Path('log')
if not log_dir.exists():
    log_dir.mkdir()
log_path = log_dir / log_name

def filter(record: "Record"):
    """默认的日志过滤器，根据 `config.log_level` 配置改变日志等级。"""
    log_level = "DEBUG"
    levelno = logger.level(log_level).no if isinstance(log_level, str) else log_level
    return record["level"].no >= levelno

logger.add(str(log_path),
           rotation='00:00',
           diagnose=False,
           filter=filter,
           format=default_format,
           encoding='utf-8')

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(OneBot_V11_Adapter)

nonebot.load_from_toml("pyproject.toml")

# Modify some config / config depends on loaded configs
#
# config = driver.config
# do something...

if __name__ == '__main__':
    logger.warning("Always use `nb run` to start the bot instead of manually running!")
    nonebot.run(app="__mp_main__:app")
