import time
import aiohttp
import asyncio
from pathlib import Path
from nonebot.log import logger

from .sub_list import get_sub_list
from .data_source import get_play_url
from .flv_checker import FlvChecker
from .utils import send_bot_msg

data_path = Path() / 'data' / 'blive'


class Recorder:
    def __init__(self, up_name, room_id):
        self.up_name: str = up_name
        self.room_id: str = room_id
        self.files: list[Path] = []
        self.files_checked: list[Path] = []
        self.recording: bool = False
        self.downloading: bool = False

    async def record(self):
        self.files = []
        self.files_checked = []
        self.recording = True
        self.downloading = True
        while self.recording:
            await self.download()
        self.downloading = False

    async def stop_and_upload(self):
        self.recording = False
        while self.downloading:
            await asyncio.sleep(1)
        await self.check()
        await self.split_files()
        urls = await self.upload()
        if urls:
            msg = f'{self.up_name} 的录播文件：\n' + '\n'.join(urls)
            await self.send_msg(msg)

    async def download(self):
        url = await get_play_url(self.room_id)
        if not url:
            return

        time_now = time.strftime('%Y%m%d_%H-%M', time.localtime())
        file_path = data_path / f'{self.up_name}_{time_now}.flv'
        self.files.append(file_path)

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'referer': 'https://live.bilibili.com/'
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=120) as resp:
                    with file_path.open('wb') as f:
                        while self.recording:
                            chunk = await resp.content.read(1024*1024)
                            if chunk:
                                f.write(chunk)
        except:
            logger.warning('Error while download live stream!')

    async def check(self):
        for file in self.files:
            if not file.exists() or file.stat().st_size < 1024 * 1024:
                continue
            file_checked = file.parent / f'{file.stem}-checked.flv'
            flv_checker = FlvChecker(file, file_checked)
            await flv_checker.check()
            self.files_checked.append(file_checked)
            try:
                file.unlink()
            except:
                pass

    async def split_files(self):
        for file in self.files_checked.copy():
            if not file.exists():
                continue
            if file.stat().st_size > 1.8 * 1024 * 1024 * 1024:
                zip_dir = file.parent / file.stem
                if not zip_dir.exists():
                    zip_dir.mkdir()
                await self.zip_file(file)
                self.files_checked.remove(file)
                for f in zip_dir.iterdir():
                    self.files_checked.append(f)

    async def upload(self):
        urls = []
        for file in self.files_checked:
            url = await self.upload_file(file)
            if url:
                urls.append(url)
        return urls

    async def zip_file(self, file: Path, zip_dir: Path):
        out = zip_dir / f'{file.stem}.zip'
        command = f'zip -s 1500m "{out.absolute()}" "{file.absolute()}"'
        print(command)
        process = await asyncio.create_subprocess_shell(command)
        await process.wait()
        return

    async def upload_file(self, path: Path):
        command = f'transfer cow -s --silent "{path.absolute()}"'
        process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await process.communicate()
        result = stdout.decode().strip()
        return result

    async def send_msg(self, msg):
        if not msg:
            return
        sub_list = get_sub_list()
        for user_id, user_sub_list in sub_list.items():
            if self.room_id in user_sub_list and user_sub_list[self.room_id]['record']:
                await send_bot_msg(user_id, msg)
