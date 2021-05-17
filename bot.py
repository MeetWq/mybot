import nonebot
from pathlib import Path
from nonebot.adapters.cqhttp import Bot as CQHTTPBot

from nonebot.log import logger, default_format

log_name = 'nonebot.log'
log_dir = Path('log')
if not log_dir.exists():
    log_dir.mkdir()
log_path = log_dir / log_name

logger.add(str(log_path),
           rotation='00:00',
           diagnose=False,
           level='DEBUG',
           format=default_format,
           encoding='utf-8')

# You can pass some keyword args config to init function
nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter('cqhttp', CQHTTPBot)

nonebot.load_plugins('src/plugins')
nonebot.load_plugin('nonebot_plugin_manager')
nonebot.load_plugin('nonebot_plugin_test')
nonebot.load_plugin('nonebot_plugin_apscheduler')

# Modify some config / config depends on loaded configs
#
# config = driver.config
# do something...

if __name__ == '__main__':
    nonebot.run()
