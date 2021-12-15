import httpx
import random
import imageio
from io import BytesIO
from lxml import etree
from typing import List
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from PIL.Image import Image as IMG
from PIL.ImageFont import FreeTypeFont
from PIL import Image, ImageFont, ImageDraw
from nonebot.adapters.cqhttp import Message, MessageSegment

from nonebot.log import logger

dir_path = Path(__file__).parent
data_path = dir_path / 'resources'

OVER_LENGTH_MSG = '文字长度过长，请适当缩减'


async def get_random_emoji(keyword: str) -> str:
    url = f'https://fabiaoqing.com/search/bqb/keyword/{quote(keyword)}/type/bq/page/1.html'
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        result = resp.text
    dom = etree.HTML(result)
    images = dom.xpath(
        "//div[@class='searchbqppdiv tagbqppdiv']/a/img/@data-original")
    if not images:
        return ''
    images = images[:3] if len(images) >= 3 else images
    return random.choice(images)


def save_jpg(frame: IMG) -> BytesIO:
    output = BytesIO()
    frame = frame.convert('RGB')
    frame.save(output, format='jpeg')
    return output


def save_png(frame: IMG) -> BytesIO:
    output = BytesIO()
    frame = frame.convert('RGBA')
    frame.save(output, format='png')
    return output


def save_gif(frames: List[IMG], duration: float) -> BytesIO:
    output = BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=duration)
    return output


def wrap_text(text: str, font: FreeTypeFont, max_width: float) -> List[str]:
    line = ''
    lines = []
    for t in text:
        if t == '\n':
            lines.append(line)
            line = ''
        elif font.getsize(line + t)[0] > max_width:
            lines.append(line)
            line = t
        else:
            line += t
    lines.append(line)
    return lines


async def make_wangjingze(texts: List[str]) -> BytesIO:
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    frames = [Image.open(data_path / f'wangjingze/{i}.jpg')
              for i in range(0, 52)]
    parts = [frames[0:9], frames[12:24], frames[25:35], frames[37:48]]
    img_w, img_h = frames[0].size
    for part, text in zip(parts, texts):
        text_w, text_h = font.getsize(text)
        if text_w > img_w - 10:
            return OVER_LENGTH_MSG
        x = int((img_w - text_w) / 2)
        y = img_h - text_h - 5
        for frame in part:
            draw = ImageDraw.Draw(frame)
            draw.text((x, y), text, font=font, fill=(255, 255, 255),
                      stroke_width=1, stroke_fill=(0, 0, 0))
    return save_gif(frames, 0.13)


async def make_weisuoyuwei(texts: List[str]) -> BytesIO:
    font = ImageFont.truetype('msyh.ttc', 15, encoding='utf-8')
    frames = [Image.open(data_path / f'weisuoyuwei/{i}.jpg')
              for i in range(0, 125)]
    parts = [frames[8:10], frames[20:27], frames[32:45], frames[46:60], frames[61:70],
             frames[72:79], frames[83:98], frames[109:118], frames[118:125]]
    img_w, img_h = frames[0].size
    for part, text in zip(parts, texts):
        text_w, text_h = font.getsize(text)
        if text_w > img_w - 10:
            return OVER_LENGTH_MSG
        x = int((img_w - text_w) / 2)
        y = img_h - text_h - 5
        for frame in part:
            draw = ImageDraw.Draw(frame)
            draw.text((x, y), text, font=font, fill=(255, 255, 255),
                      stroke_width=1, stroke_fill=(0, 0, 0))
    return save_gif(frames, 0.17)


async def make_ninajiaoxihuanma(texts: List[str]) -> BytesIO:
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    frames = [Image.open(data_path / f'ninajiaoxihuanma/{i}.jpg')
              for i in range(0, 58)]
    parts = [frames[5:22], frames[26:38], frames[39:50]]
    img_w, img_h = frames[0].size
    for part, text in zip(parts, texts):
        text_w, text_h = font.getsize(text)
        if text_w > img_w - 10:
            return OVER_LENGTH_MSG
        x = int((img_w - text_w) / 2)
        y = img_h - text_h - 5
        for frame in part:
            draw = ImageDraw.Draw(frame)
            draw.text((x, y), text, font=font, fill=(255, 255, 255),
                      stroke_width=1, stroke_fill=(0, 0, 0))
    return save_gif(frames, 0.1)


async def make_qiegewala(texts: List[str]) -> BytesIO:
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    frames = [Image.open(data_path / f'qiegewala/{i}.jpg')
              for i in range(0, 87)]
    parts = [frames[0:15], frames[16:31], frames[31:38],
             frames[38:48], frames[49:68], frames[68:86]]
    img_w, img_h = frames[0].size
    for part, text in zip(parts, texts):
        text_w, text_h = font.getsize(text)
        if text_w > img_w - 10:
            return OVER_LENGTH_MSG
        x = int((img_w - text_w) / 2)
        y = img_h - text_h - 5
        for frame in part:
            draw = ImageDraw.Draw(frame)
            draw.text((x, y), text, font=font, fill=(255, 255, 255),
                      stroke_width=1, stroke_fill=(0, 0, 0))
    return save_gif(frames, 0.13)


async def make_luxunsay(texts: List[str]) -> BytesIO:
    font = ImageFont.truetype('msyh.ttc', 38, encoding='utf-8')
    luxun_font = ImageFont.truetype('msyh.ttc', 30, encoding='utf-8')
    lines = wrap_text(texts[0], font, 430)
    if len(lines) > 2:
        return OVER_LENGTH_MSG
    text = '\n'.join(lines)
    spacing = 5
    text_w, text_h = font.getsize_multiline(text, spacing=spacing)
    frame = Image.open(data_path / f'luxunsay/0.jpg')
    img_w, img_h = frame.size
    x = int((img_w - text_w) / 2)
    y = int((img_h - text_h) / 2) + 110
    draw = ImageDraw.Draw(frame)
    draw.multiline_text((x, y), text, font=font,
                        align='center', spacing=spacing, fill=(255, 255, 255))
    draw.text((320, 400), '--鲁迅', font=luxun_font, fill=(255, 255, 255))
    return save_png(frame)


async def make_nokia(texts: List[str]) -> BytesIO:
    font = ImageFont.truetype('方正像素14.ttf', 70, encoding='utf-8')
    lines = wrap_text(texts[0][:900], font, 700)[:5]
    text = '\n'.join(lines)
    angle = -9.3

    img_text = Image.new('RGBA', (700, 450))
    draw = ImageDraw.Draw(img_text)
    draw.multiline_text((0, 0), text, font=font,
                        spacing=30, fill=(0, 0, 0, 255))
    img_text = img_text.rotate(angle, expand=True)

    head = f'{len(text)}/900'
    img_head = Image.new('RGBA', font.getsize(head))
    draw = ImageDraw.Draw(img_head)
    draw.text((0, 0), head, font=font, fill=(129, 212, 250, 255))
    img_head = img_head.rotate(angle, expand=True)

    frame = Image.open(data_path / f'nokia/0.jpg')
    frame.paste(img_text, (205, 330), mask=img_text)
    frame.paste(img_head, (790, 320), mask=img_head)
    return save_jpg(frame)


async def make_goodnews(texts: List[str]) -> BytesIO:
    font = ImageFont.truetype('msyh.ttc', 45, encoding='utf-8')
    lines = wrap_text(texts[0], font, 480)
    if len(lines) > 5:
        return OVER_LENGTH_MSG
    text = '\n'.join(lines)
    spacing = 8
    stroke_width = 3
    text_w, text_h = font.getsize_multiline(text, spacing=spacing,
                                            stroke_width=stroke_width)
    frame = Image.open(data_path / f'goodnews/0.jpg')
    img_w, img_h = frame.size
    x = int((img_w - text_w) / 2)
    y = int((img_h - text_h) / 2)
    draw = ImageDraw.Draw(frame)
    draw.multiline_text((x, y), text, font=font,
                        align='center', spacing=spacing, fill=(238, 0, 0),
                        stroke_width=stroke_width, stroke_fill=(255, 255, 153))
    return save_png(frame)


async def make_jichou(texts: List[str]) -> BytesIO:
    text = f"今天是{datetime.today().strftime('%Y年%m月%d日')}\n{texts[0]}\n这个仇我先记下了"
    font = ImageFont.truetype('msyh.ttc', 36, encoding='utf-8')
    lines = wrap_text(text, font, 440)
    text = '\n'.join(lines)
    spacing = 10
    _, text_h = font.getsize_multiline(text, spacing=spacing)
    frame = Image.open(data_path / f'jichou/0.png')
    img_w, img_h = frame.size
    bg = Image.new('RGB', (img_w, img_h + text_h + 20), (255, 255, 255))
    bg.paste(frame, (0, 0))
    draw = ImageDraw.Draw(bg)
    draw.multiline_text((30, img_h + 5), text, font=font,
                        spacing=spacing, fill=(0, 0, 0))
    return save_jpg(bg)


emojis = {
    'wangjingze': {
        'aliases': {'王境泽'},
        'func': make_wangjingze,
        'arg_num': 4
    },
    'weisuoyuwei': {
        'aliases': {'为所欲为'},
        'func': make_weisuoyuwei,
        'arg_num': 9
    },
    'ninajiaoxihuanma': {
        'aliases': {'你那叫喜欢吗'},
        'func': make_ninajiaoxihuanma,
        'arg_num': 3
    },
    'qiegewala': {
        'aliases': {'切格瓦拉'},
        'func': make_qiegewala,
        'arg_num': 6
    },
    'luxunsay': {
        'aliases': {'鲁迅说', '鲁迅说过'},
        'func': make_luxunsay,
        'arg_num': 1
    },
    'nokia': {
        'aliases': {'诺基亚'},
        'func': make_nokia,
        'arg_num': 1
    },
    'goodnews': {
        'aliases': {'喜报'},
        'func': make_goodnews,
        'arg_num': 1
    },
    'jichou': {
        'aliases': {'记仇'},
        'func': make_jichou,
        'arg_num': 1
    }
}


async def make_emoji(type: str, texts: List[str]) -> Message:
    try:
        result = await emojis[type]['func'](texts)
        if isinstance(result, str):
            return result
        else:
            return MessageSegment.image(result)
    except Exception as e:
        logger.warning(f"Error in make_emoji({type}, {texts}): {e}")
        return None
