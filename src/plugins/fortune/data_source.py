import uuid
import json
import base64
import random
from pathlib import Path
from datetime import datetime
from src.utils.functions import trim_image
from src.utils.playwright import get_new_page
from nonebot.adapters.cqhttp import MessageSegment

dir_path = Path(__file__).parent
cache_path = Path('cache/fortune')
if not cache_path.exists():
    cache_path.mkdir(parents=True)


async def get_response(group_id, user_id, username):
    date = datetime.now().strftime('%Y%m%d')
    log_path = cache_path / (date + '_' + str(group_id) + '.log')
    log_path.touch()
    with log_path.open('r+') as f:
        logs = f.readlines()
        logs = [l.strip() for l in logs]
        if str(user_id) not in logs:
            f.write(str(user_id) + '\n')
            copywriting = get_copywriting()
            luck = copywriting['luck']
            content = copywriting['content']
            type = get_type(luck)
            face = get_face(luck)
            img_path = await create_image(username, type, content, face)
            if img_path:
                return MessageSegment.image(file='file://' + str(img_path))
            else:
                return '出错了，请稍后再试'
        else:
            return '你今天已经抽过签了，请明天再来~'


def get_copywriting():
    path = dir_path / 'copywriting.json'
    with path.open('r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['copywriting'])


def get_type(luck):
    path = dir_path / 'types.json'
    with open(path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    types = data['types']
    for type in types:
        if luck == type['luck']:
            return type['name']


def get_face(luck):
    image_path = Path('src/data/images/cc98')
    if luck in [10, 26]:
        face_id = '04'
    elif luck in [9, 20]:
        face_id = '05'
    elif luck in [8, 21, 22]:
        face_id = '02'
    elif luck in [7, 27]:
        face_id = '09'
    elif luck in [6, 24]:
        face_id = '06'
    elif luck in [5, 25]:
        face_id = '07'
    elif luck in [4, 23]:
        face_id = '10'
    elif luck in [-6]:
        face_id = '03'
    elif luck in [-7]:
        face_id = '01'
    elif luck in [-8]:
        face_id = '11'
    elif luck in [-9]:
        face_id = '08'
    elif luck in [-10]:
        face_id = '12'
    return image_path / f'cc98{face_id}.png'


async def create_image(username, fortune, content, face_path):
    html_path = dir_path / 'fortune.html'
    bg_path = dir_path / 'summer.png'
    img_name = uuid.uuid1().hex
    img_path = (cache_path / (img_name + '.png')).absolute()
    out_path = (cache_path / (img_name + '.jpg')).absolute()

    with bg_path.open('rb') as f:
        bg_b64 = 'data:image/png;base64,' + str(base64.b64encode(f.read()), 'utf-8')

    with face_path.open('rb') as f:
        face_b64 = 'data:image/png;base64,' + str(base64.b64encode(f.read()), 'utf-8')

    with html_path.open('r', encoding='utf-8') as f:
        html = f.read()
        html = html.replace('USERNAME', username).replace('FORTUNE', fortune) \
                   .replace('CONTENT', content).replace('FACE', face_b64).replace('BACKGROUND', bg_b64)

    async with get_new_page(viewport={"width": 2000,"height": 500}) as page:
        await page.set_content(html)
        await page.screenshot(path=str(img_path))

    if await trim_image(img_path, out_path):
        return out_path
    return None
