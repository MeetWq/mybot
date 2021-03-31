import os
import time
import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot

from nonebot.log import logger, default_format

if not os.path.exists('log'):
    os.makedirs('log')

log_name = 'log/' + time.strftime('nonebot_%Y%m%d', time.localtime()) + '.log'

logger.add(log_name,
           level="DEBUG",
           format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

nonebot.load_plugins("src/plugins")
nonebot.load_plugin("nonebot_plugin_manager")

# Modify some config / config depends on loaded configs
# 
# config = driver.config
# do something...


if __name__ == "__main__":
    nonebot.run(app="bot:app")
