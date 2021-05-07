import os
import uuid
import aiohttp
import subprocess
from typing import Any
from pathlib import Path


async def download(url: str, file_path: Path = None, dir_path: Path = None, **kwargs: Any):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, **kwargs) as resp:
                result = await resp.read()
        if not file_path:
            file_path = dir_path / (f"{uuid.uuid1().hex}.{url.split('.')[-1]}")
        with file_path.open('wb') as f:
            f.write(result)
        return file_path
    except:
        return None


async def trim_image(input_path: Path, output_path: Path, args: str = ''):
    try:
        stdout = open(os.devnull, 'w')
        p_open = subprocess.Popen(f'convert {input_path} -trim {args} {output_path}',
                                  shell=True, stdout=stdout, stderr=stdout)
        p_open.wait()
        stdout.close()
        if p_open.returncode != 0:
            return False
        return True
    except:
        return False
