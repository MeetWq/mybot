from os import path
import nonebot
import config
import logging
from nonebot.log import logger

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(path.join(path.dirname(__file__), 'my', 'plugins'), 'my.plugins')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(path.join('my', 'log', 'nonebot.log'))
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s %(name)s] %(levelname)s: %(message)s'
    ))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    nonebot.run()
