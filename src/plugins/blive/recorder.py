import time
import requests
import traceback
from typing import List
from pathlib import Path
from nonebot.log import logger

from .flv_checker import FlvChecker
from .aliyun import upload_and_share

data_path = Path() / 'data' / 'blive'


class Recorder:
    def __init__(self, up_name, play_url):
        self.up_name: str = up_name
        self.play_url: str = play_url
        self.files: list[Path] = []
        self.urls: list[str] = []
        self.recording: bool = False
        self.uploading: bool = False
        self.need_update_url: bool = False

    def record(self):
        self.recording = True
        logger.info(f'{self.up_name} record start')
        while self.recording:
            if not self.download():
                self.need_update_url = True
            delay = 30
            for i in range(delay):
                if not self.recording:
                    break
                time.sleep(1)
        logger.info(f'{self.up_name} record stop')

    def upload(self):
        self.uploading = True
        files = self.files.copy()
        self.files = []
        time.sleep(10)
        files_checked = self.check_files(files)
        self.upload_files(files_checked)

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
                    return True
                except:
                    logger.warning(
                        f'Error while download live stream! retry {i}/{retry}' + traceback.format_exc())
        return False

    def check_files(self, files: List[Path]) -> List[Path]:
        files_checked = []
        for file in files:
            if not file.exists() or file.stat().st_size < 10 * 1024 * 1024:
                file.unlink(missing_ok=True)
                continue
            file_checked = file.parent / file.name.replace('-raw.flv', '.flv')
            flv_checker = FlvChecker(file, file_checked)
            flv_checker.check()
            logger.info(f'{file} checked')
            files_checked.append(file_checked)
            # file.unlink(missing_ok=True)
        return files_checked

    def upload_files(self, files_checked: List[Path]):
        for file in files_checked:
            if not file.exists():
                continue
            try:
                url = upload_and_share(file, f'records/{self.up_name}')
            except:
                logger.warning(f'upload {file} failed')
                logger.warning(traceback.format_exc())
                continue

            if url:
                logger.info(f'upload {file} done, url: {url}')
                self.urls.append(url)
                file.unlink(missing_ok=True)
            else:
                logger.warning(f'upload {file} failed!')
        self.uploading = False
