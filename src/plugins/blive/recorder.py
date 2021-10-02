import os
import time
import asyncio
import requests
import traceback
from pathlib import Path
from typing import Coroutine
from nonebot import get_driver
from nonebot.log import logger

from .sub_list import get_sub_list
from .data_source import get_play_url
from .flv_checker import FlvChecker
from .utils import send_bot_msg

from .config import Config
global_config = get_driver().config
blive_config = Config(**global_config.dict())

data_path = Path() / 'data' / 'blive'

try:
    os.environ['ALIYUNPAN_ROOT'] = str((Path('log')).absolute())
    from aliyunpan.cli.cli import Commander
    commander = Commander(refresh_token=blive_config.aliyunpan_refresh_token)
except:
    commander = None


def sync(coroutine: Coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)


class Recorder:
    def __init__(self, up_name, room_id):
        self.up_name: str = up_name
        self.room_id: str = room_id
        self.files: list[Path] = []
        self.files_checked: list[Path] = []
        self.recording: bool = False
        self.downloading: bool = False
        self.retry = 5

    def record(self):
        self.files = []
        self.files_checked = []
        self.recording = True
        self.downloading = True
        logger.info(f'{self.up_name} record start')
        sync(self.send_msg(f'{self.up_name} 录制启动...'))
        while self.recording:
            self.download()
            delay = 60
            for i in range(delay):
                if not self.recording:
                    break
                time.sleep(1)
        self.downloading = False
        logger.info(f'{self.up_name} record stop')

    def stop_and_upload(self):
        self.recording = False
        while self.downloading:
            time.sleep(1)
        self.check()
        urls = self.upload()
        if urls:
            msg = f'{self.up_name} 的录播文件：\n' + '\n'.join(urls)
            logger.info(msg)
            sync(self.send_msg(msg))
            for file in self.files_checked:
                file.unlink(missing_ok=True)


    def download(self):
        logger.info(f'start download')
        url = get_play_url(self.room_id)
        logger.info(f'{self.up_name} play url: {url}')
        if not url:
            return

        time_now = time.strftime('%Y%m%d_%H-%M', time.localtime())
        file_path = data_path / f'{self.up_name}_{time_now}.flv'
        self.files.append(file_path)

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'referer': 'https://live.bilibili.com/'
        }
        with file_path.open('wb') as f:
            for i in range(self.retry):
                try:
                    resp = requests.get(
                        url, stream=True, headers=headers, timeout=300)
                    for data in resp.iter_content(chunk_size=1024*1024):
                        if not self.recording:
                            break
                        if data:
                            f.write(data)
                    resp.close()
                except:
                    logger.warning(
                        'Error while download live stream!' + traceback.format_exc())

    def check(self):
        for file in self.files:
            logger.info(f'{file} filesize: {file.stat().st_size}')
            if not file.exists() or file.stat().st_size < 1024 * 1024:
                file.unlink(missing_ok=True)
                continue
            file_checked = file.parent / f'{file.stem}-checked.flv'
            flv_checker = FlvChecker(file, file_checked)
            flv_checker.check()
            logger.info(f'{file} checked')
            self.files_checked.append(file_checked)
            file.unlink(missing_ok=True)

    def upload(self):
        urls = []
        for file in self.files_checked:
            url = self.upload_file(file)
            if url:
                logger.info(f'upload {file} done, url: {url}')
                urls.append(url)
        return urls

    def upload_file(self, path: Path):
        if not commander:
            return ''
        if not path.exists():
            return ''
        try:
            upload_path = f'records/{self.up_name}'
            commander.mkdir(upload_path)
            logger.info(f'upload {path} to {upload_path} ...')
            commander.upload(str(path.absolute()), upload_path)
            logger.info(f'upload {path} to {upload_path} successfully')
            expiration = 24 * 3600
            upload_name = f'{upload_path}/{path.name}'
            file_id_list = [commander._path_list.get_path_fid(
                upload_name, update=False)]
            if file_id_list:
                url = commander._disk.share_link(
                    file_id_list, time.time() + expiration)
                return url
            return ''
        except:
            logger.warning(f'upload to aliyunpan failed')
            return ''

    async def send_msg(self, msg):
        if not msg:
            return
        sub_list = get_sub_list()
        for user_id, user_sub_list in sub_list.items():
            if self.room_id in user_sub_list and user_sub_list[self.room_id]['record']:
                await send_bot_msg(user_id, msg)
