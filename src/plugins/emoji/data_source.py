import re
import uuid
import random
import aiohttp
import traceback
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote
from PIL import Image, ImageFont, ImageDraw
from nonebot.adapters.cqhttp import MessageSegment

from nonebot.log import logger

image_path = Path('src/data/images')
cache_path = Path('cache/emoji').absolute()
if not cache_path.exists():
    cache_path.mkdir(parents=True)


def get_emoji_path(name: str):
    patterns = [
        (r'(ac\d{2,4})', 'ac', lambda x: x.group(1)),
        (r'(em\d{2})', 'em', lambda x: x.group(1)),
        (r'emm(\d{1,3})', 'nhd', lambda x: 'em' + x.group(1)),
        (r'([acf]:?\d{3})', 'mahjong', lambda x: x.group(1)),
        (r'(ms\d{2})', 'ms', lambda x: x.group(1)),
        (r'(tb\d{2})', 'tb', lambda x: x.group(1)),
        (r'([Cc][Cc]98\d{2})', 'cc98', lambda x: x.group(1))
    ]

    name = name.strip().split('.')[0].replace(':', '').lower()
    file_ext = ['.jpg', '.png', '.gif']
    for pattern, dir_name, func in patterns:
        if re.match(pattern, name):
            name = re.sub(pattern, func, name)
            for ext in file_ext:
                file_path = image_path / dir_name / (name + ext)
                if file_path.exists():
                    return str(file_path.absolute())
    return None


async def get_image(keyword):
    url = f'https://fabiaoqing.com/search/bqb/keyword/{quote(keyword)}/type/bq/page/1.html'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = await resp.text()

    result = BeautifulSoup(result, 'lxml')
    images = result.find_all('div', {'class': 'searchbqppdiv tagbqppdiv'})
    image_num = len(images)
    if image_num <= 0:
        return ''
    if image_num >= 3:
        images = images[:3]
    return random.choice(images).img['data-original']


def text_position(image, text, font, padding_y=5):
    text_width, text_height = font.getsize(text)
    img_width, img_height = image.size
    x = int((img_width - text_width) / 2)
    y = img_height - text_height - padding_y
    return x, y


async def darw_text(image, x, y, text, font, shadowcolor, fillcolor):
    draw = ImageDraw.Draw(image)
    # thin border
    draw.text((x - 1, y), text, font=font, fill=shadowcolor)
    draw.text((x + 1, y), text, font=font, fill=shadowcolor)
    draw.text((x, y - 1), text, font=font, fill=shadowcolor)
    draw.text((x, y + 1), text, font=font, fill=shadowcolor)
    # thicker border
    draw.text((x - 1, y - 1), text, font=font, fill=shadowcolor)
    draw.text((x + 1, y - 1), text, font=font, fill=shadowcolor)
    draw.text((x - 1, y + 1), text, font=font, fill=shadowcolor)
    draw.text((x + 1, y + 1), text, font=font, fill=shadowcolor)
    # now draw the text over it
    draw.text((x, y), text, font=font, fill=fillcolor)


async def make_wangjingze(texts):
    font_path = Path('src/data/fonts/msyh.ttc')
    font = ImageFont.truetype(str(font_path), 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    files = [Path('src/data/emojis/wangjingze/%d.jpg' % i) for i in range(0, 52)]
    frames = [Image.open(f) for f in files]
    parts = [frames[0:9], frames[12:24], frames[25:35], frames[37:48]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return f'“{text}”长度过长，请适当缩减'
            await darw_text(frame, x, y, text, font, shadowcolor, fillcolor)
    save_path = cache_path / (uuid.uuid1().hex + '.gif')
    frames[0].save(save_path, save_all=True, append_images=frames[1:], duration=130)
    return MessageSegment.image(file=f'file://{save_path}')


async def make_weisuoyuwei(texts):
    font_path = Path('src/data/fonts/msyh.ttc')
    font = ImageFont.truetype(str(font_path), 15, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    files = [Path('src/data/emojis/weisuoyuwei/%d.jpg' % i) for i in range(0, 125)]
    frames = [Image.open(f) for f in files]
    parts = [frames[8:10], frames[20:27], frames[32:45], frames[46:60],
             frames[61:70], frames[72:79], frames[83:98], frames[109:118], frames[118:125]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return f'“{text}”长度过长，请适当缩减'
            await darw_text(frame, x, y, text, font, shadowcolor, fillcolor)
    save_path = cache_path / (uuid.uuid1().hex + '.gif')
    frames[0].save(save_path, save_all=True, append_images=frames[1:], duration=170)
    return MessageSegment.image(file=f'file://{save_path}')


async def make_ninajiaoxihuanma(texts):
    font_path = Path('src/data/fonts/msyh.ttc')
    font = ImageFont.truetype(str(font_path), 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    files = [Path('src/data/emojis/ninajiaoxihuanma/%d.jpg' % i) for i in range(0, 58)]
    frames = [Image.open(f) for f in files]
    parts = [frames[5:22], frames[26:38], frames[39:50]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return f'“{text}”长度过长，请适当缩减'
            await darw_text(frame, x, y, text, font, shadowcolor, fillcolor)
    save_path = cache_path / (uuid.uuid1().hex + '.gif')
    frames[0].save(save_path, save_all=True, append_images=frames[1:], duration=100)
    return MessageSegment.image(file=f'file://{save_path}')


async def make_qiegewala(texts):
    font_path = Path('src/data/fonts/msyh.ttc')
    font = ImageFont.truetype(str(font_path), 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    files = [Path('src/data/emojis/qiegewala/%d.jpg' % i) for i in range(0, 87)]
    frames = [Image.open(f) for f in files]
    parts = [frames[0:15], frames[16:31], frames[31:38], 
             frames[38:48], frames[49:68], frames[68:86]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return f'“{text}”长度过长，请适当缩减'
            await darw_text(frame, x, y, text, font, shadowcolor, fillcolor)
    save_path = cache_path / (uuid.uuid1().hex + '.gif')
    frames[0].save(save_path, save_all=True, append_images=frames[1:], duration=130)
    return MessageSegment.image(file=f'file://{save_path}')


emojis = [
    {
        'names': ['王境泽', '真香'],
        'input_num': 4,
        'func': make_wangjingze,
    },
    {
        'names': ['为所欲为'],
        'input_num': 9,
        'func': make_weisuoyuwei,
    },
    {
        'names': ['你那叫喜欢吗'],
        'input_num': 3,
        'func': make_ninajiaoxihuanma,
    },
    {
        'names': ['切格瓦拉', '打工是不可能打工的'],
        'input_num': 6,
        'func': make_qiegewala,
    }
]


async def make_emoji(num, texts):
    try:
        msg = await emojis[num]['func'](texts)
        return msg
    except:
        logger.debug(traceback.format_exc())
        return '出错了，请稍后再试'
