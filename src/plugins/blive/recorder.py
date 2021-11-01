import os
import time
import asyncio
import requests
import traceback
from pathlib import Path
from typing import Coroutine
from nonebot import get_driver
from nonebot.log import logger

from .flv_checker import FlvChecker

from .config import Config
global_config = get_driver().config
blive_config = Config(**global_config.dict())

data_path = Path() / 'data' / 'blive'

try:
    os.environ['ALIYUNPAN_ROOT'] = str((Path('log')).absolute())
    from aliyunpan.cli.cli import Commander
    commander = Commander(refresh_token=blive_config.aliyunpan_refresh_token, filter_file=set())
except:
    commander = None


def sync(coroutine: Coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)


class Recorder:
    def __init__(self, up_name, play_url):
        self.up_name: str = up_name
        self.play_url: str = play_url
        self.files: list[Path] = []
        self.files_checked: list[Path] = []
        self.urls: list[str] = []
        self.recording: bool = False
        self.uploading: bool = False

    def record(self):
        self.recording = True
        logger.info(f'{self.up_name} record start')
        while self.recording:
            self.download()
            delay = 60
            for i in range(delay):
                if not self.recording:
                    break
                time.sleep(1)
        logger.info(f'{self.up_name} record stop')

    def stop(self):
        self.recording = False

    def stop_and_upload(self):
        self.recording = False
        self.uploading = True
        time.sleep(10)
        self.check_files()
        self.upload_files()

    def download(self):
        time_now = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        file_path = data_path / f'{self.up_name}_{time_now}-raw.flv'
        self.files.append(file_path)
        logger.info(f'start download {file_path}')

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'referer': 'https://live.bilibili.com/'
        }
        with file_path.open('wb') as f:
            retry = 5
            for i in range(retry):
                try:
                    resp = requests.get(
                        self.play_url, stream=True, headers=headers, timeout=300)
                    if resp.status_code != 200 or not resp.headers['Content-Type'].startswith('video/'):
                        continue
                    for data in resp.iter_content(chunk_size=1024*1024):
                        if not self.recording:
                            break
                        if data:
                            f.write(data)
                    resp.close()
                except:
                    logger.warning(
                        f'Error while download live stream! retry {i}/{retry}' + traceback.format_exc())

    def check_files(self):
        for file in self.files:
            if not file.exists() or file.stat().st_size < 10 * 1024 * 1024:
                file.unlink(missing_ok=True)
                continue
            file_checked = file.parent / file.name.replace('-raw.flv', '.flv')
            flv_checker = FlvChecker(file, file_checked)
            flv_checker.check()
            logger.info(f'{file} checked')
            self.files_checked.append(file_checked)
            # file.unlink(missing_ok=True)

    def upload_files(self):
        for file in self.files_checked:
            url = self.upload_file(file)
            if url:
                logger.info(f'upload {file} done, url: {url}')
                self.urls.append(url)
                file.unlink(missing_ok=True)
            else:
                logger.warning(f'upload {file} failed!')
        self.uploading = False

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
                logger.info(f'create share link for {upload_name}, url: {url}')
                return url
            return ''
        except:
            logger.warning(f'upload to aliyunpan failed')
            return ''
