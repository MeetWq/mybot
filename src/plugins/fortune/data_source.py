import io
import json
import base64
import jinja2
import random
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageChops
from src.libs.playwright import get_new_page
from nonebot.adapters.cqhttp import MessageSegment

dir_path = Path(__file__).parent
template_path = dir_path / 'template'
data_path = Path('data/fortune')
if not data_path.exists():
    data_path.mkdir(parents=True)


async def get_response(user_id, username):
    try:
        log_path = data_path / (datetime.now().strftime('%Y%m%d') + '.json')
        if log_path.exists():
            log = json.load(log_path.open('r', encoding='utf-8'))
        else:
            log = {}

        if user_id not in log:
            copywriting = get_copywriting()
            luck = copywriting['luck']
            content = copywriting['content']
            fortune = get_type(luck)
            face = get_face(luck)
            image = await create_image(username, luck, fortune, content, face)
            if image:
                log[user_id] = fortune
                json.dump(log, log_path.open('w', encoding='utf-8'), ensure_ascii=False)
                return MessageSegment.image(f"base64://{base64.b64encode(image).decode()}")
        else:
            fortune = log[user_id]
            return '你今天已经抽过签了，你的今日运势是：' + fortune
    except:
        return '出错了，请稍后再试'


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
    if luck in [10]:
        face_id = '04'
    elif luck in [9, 20]:
        face_id = '05'
    elif luck in [8, 26]:
        face_id = '09'
    elif luck in [7, 27]:
        face_id = '07'
    elif luck in [6, 25]:
        face_id = '10'
    elif luck in [5]:
        face_id = '03'
    elif luck in [4]:
        face_id = '01'
    elif luck in [21, 22]:
        face_id = '02'
    elif luck in [23, 24]:
        face_id = '06'
    elif luck in [-6]:
        face_id = '08'
    elif luck in [-7]:
        face_id = '11'
    elif luck in [-8, -9, -10]:
        face_id = '12'
    return f'cc98{face_id}.png'


def load_jpg(name):
   with (template_path / name).open('rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()


def load_png(name):
   with (template_path / name).open('rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


async def create_image(username, luck, fortune, content, face):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_path.absolute())))
    env.filters['load_jpg'] = load_jpg
    env.filters['load_png'] = load_png
    template = env.get_template('fortune.html')

    if len(username) > 50:
        username = username[:50] + '...'
    html = template.render(username=username, luck=luck, fortune=fortune, content=content, face=face)

    async with get_new_page(viewport={"width": 2000,"height": 500}) as page:
        await page.set_content(html)
        raw_image = await page.screenshot()

    return await trim(raw_image, format='jpeg')


async def trim(im, format='png'):
    im = Image.open(io.BytesIO(im)).convert('RGB')
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    box = diff.getbbox()
    if box:
        im = im.crop(box)
    output = io.BytesIO()
    im.save(output, format=format)
    return output.getvalue()
