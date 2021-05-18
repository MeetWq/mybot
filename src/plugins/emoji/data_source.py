import io
import re
import base64
import random
import aiohttp
import imageio
import traceback
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote
from PIL import Image, ImageFont, ImageDraw
from nonebot.adapters.cqhttp import MessageSegment

from nonebot.log import logger

dir_path = Path(__file__).parent
emoji_path = dir_path / 'emojis'
gif_path = dir_path / 'gifs'


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
                file_path = emoji_path / dir_name / (name + ext)
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
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    files = [gif_path / 'wangjingze' / ('%d.jpg' % i) for i in range(0, 52)]
    frames = [Image.open(f) for f in files]
    parts = [frames[0:9], frames[12:24], frames[25:35], frames[37:48]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return f'“{text}”长度过长，请适当缩减'
            await darw_text(frame, x, y, text, font, shadowcolor, fillcolor)
    gif_file = io.BytesIO()
    imageio.mimsave(gif_file, frames, format='gif', duration=0.13)
    return MessageSegment.image(f"base64://{base64.b64encode(gif_file.getvalue()).decode()}")


async def make_weisuoyuwei(texts):
    font = ImageFont.truetype('msyh.ttc', 15, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    files = [gif_path / 'weisuoyuwei' / ('%d.jpg' % i) for i in range(0, 125)]
    frames = [Image.open(f) for f in files]
    parts = [frames[8:10], frames[20:27], frames[32:45], frames[46:60],
             frames[61:70], frames[72:79], frames[83:98], frames[109:118], frames[118:125]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return f'“{text}”长度过长，请适当缩减'
            await darw_text(frame, x, y, text, font, shadowcolor, fillcolor)
    gif_file = io.BytesIO()
    imageio.mimsave(gif_file, frames, format='gif', duration=0.17)
    return MessageSegment.image(f"base64://{base64.b64encode(gif_file.getvalue()).decode()}")


async def make_ninajiaoxihuanma(texts):
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    files = [gif_path / 'ninajiaoxihuanma' / ('%d.jpg' % i) for i in range(0, 58)]
    frames = [Image.open(f) for f in files]
    parts = [frames[5:22], frames[26:38], frames[39:50]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return f'“{text}”长度过长，请适当缩减'
            await darw_text(frame, x, y, text, font, shadowcolor, fillcolor)
    gif_file = io.BytesIO()
    imageio.mimsave(gif_file, frames, format='gif', duration=0.1)
    return MessageSegment.image(f"base64://{base64.b64encode(gif_file.getvalue()).decode()}")


async def make_qiegewala(texts):
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    files = [gif_path / 'qiegewala' / ('%d.jpg' % i) for i in range(0, 87)]
    frames = [Image.open(f) for f in files]
    parts = [frames[0:15], frames[16:31], frames[31:38], 
             frames[38:48], frames[49:68], frames[68:86]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return f'“{text}”长度过长，请适当缩减'
            await darw_text(frame, x, y, text, font, shadowcolor, fillcolor)
    gif_file = io.BytesIO()
    imageio.mimsave(gif_file, frames, format='gif', duration=0.13)
    return MessageSegment.image(f"base64://{base64.b64encode(gif_file.getvalue()).decode()}")


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
