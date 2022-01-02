import os
import time
from pathlib import Path
from aliyunpan.cli.cli import Commander
from nonebot import get_driver
from nonebot.log import logger

from .config import Config
global_config = get_driver().config
blive_config = Config(**global_config.dict())

token_path = Path() / 'data' / 'blive' / 'refresh_token.txt'


def get_refresh_token() -> str:
    if not token_path.exists():
        token = blive_config.aliyunpan_refresh_token
        dump_refresh_token(token)
    else:
        token = load_refresh_token()
    return token


def load_refresh_token() -> str:
    with token_path.open('r', encoding='utf-8') as f:
        return f.read()


def dump_refresh_token(token: str):
    with token_path.open('w', encoding='utf-8') as f:
        f.write(token)


def load_aliyunpan_cli() -> Commander:
    os.environ['ALIYUNPAN_ROOT'] = str((Path('log')).absolute())
    from aliyunpan.cli.cli import Commander
    return Commander(refresh_token=get_refresh_token())


def update_refresh_token():
    commander = load_aliyunpan_cli()
    commander.disk.token_refresh()
    token = commander.disk.refresh_token
    dump_refresh_token(token)


def upload_and_share(file_path: Path, upload_path: str, expiration: int = 24 * 3600) -> str:
    commander = load_aliyunpan_cli()
    commander.mkdir(upload_path)
    logger.info(f'upload {file_path} to {upload_path} ...')
    commander.upload(str(file_path.absolute()), upload_path)
    logger.info(f'upload {file_path} to {upload_path} successfully')
    time.sleep(30)
    upload_name = f'{upload_path}/{file_path.name}'
    fids = [commander.path_list.get_path_fid(upload_name, update=False)]
    if fids:
        url = commander.disk.share_link(fids, time.time() + expiration)
        logger.info(f'create share link for {upload_name}, url: {url}')
        return url
    return ''
