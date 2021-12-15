import math
import httpx
import random
import imageio
from io import BytesIO
from lxml import etree
from typing import List
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageFont, ImageDraw
from nonebot.adapters.cqhttp import Message, MessageSegment

from nonebot.log import logger

dir_path = Path(__file__).parent
data_path = dir_path / 'resources'


async def get_random_emoji(keyword):
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


def text_position(image, text, font, padding_y=5):
    text_width, text_height = font.getsize(text)
    img_width, img_height = image.size
    x = int((img_width - text_width) / 2)
    y = img_height - text_height - padding_y
    return x, y


def darw_text(draw, x, y, text, font, fillcolor, shadowcolor=None, border=1):
    if shadowcolor:
        # thin border
        draw.text((x - border, y), text, font=font, fill=shadowcolor)
        draw.text((x + border, y), text, font=font, fill=shadowcolor)
        draw.text((x, y - border), text, font=font, fill=shadowcolor)
        draw.text((x, y + border), text, font=font, fill=shadowcolor)
        # thicker border
        draw.text((x - border, y - border), text, font=font, fill=shadowcolor)
        draw.text((x + border, y - border), text, font=font, fill=shadowcolor)
        draw.text((x - border, y + border), text, font=font, fill=shadowcolor)
        draw.text((x + border, y + border), text, font=font, fill=shadowcolor)
    # now draw the text over it
    draw.text((x, y), text, font=font, fill=fillcolor)


def wrap_text(text, font, max_width):
    line = ''
    lines = []
    for t in text:
        if font.getsize(line + t)[0] > max_width:
            lines.append(line)
            line = t
        else:
            line += t
    lines.append(line)
    return lines


async def make_wangjingze(texts) -> BytesIO:
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    frames = [Image.open(data_path / f'wangjingze/{i}.jpg')
              for i in range(0, 52)]
    parts = [frames[0:9], frames[12:24], frames[25:35], frames[37:48]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return '文字长度过长，请适当缩减'
            draw = ImageDraw.Draw(frame)
            darw_text(draw, x, y, text, font, fillcolor, shadowcolor)
    output = BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=0.13)
    return output


async def make_weisuoyuwei(texts) -> BytesIO:
    font = ImageFont.truetype('msyh.ttc', 15, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    frames = [Image.open(data_path / f'weisuoyuwei/{i}.jpg')
              for i in range(0, 125)]
    parts = [frames[8:10], frames[20:27], frames[32:45], frames[46:60], frames[61:70],
             frames[72:79], frames[83:98], frames[109:118], frames[118:125]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return '文字长度过长，请适当缩减'
            draw = ImageDraw.Draw(frame)
            darw_text(draw, x, y, text, font, fillcolor, shadowcolor)
    output = BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=0.17)
    return output


async def make_ninajiaoxihuanma(texts):
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    frames = [Image.open(data_path / f'ninajiaoxihuanma/{i}.jpg')
              for i in range(0, 58)]
    parts = [frames[5:22], frames[26:38], frames[39:50]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return '文字长度过长，请适当缩减'
            draw = ImageDraw.Draw(frame)
            darw_text(draw, x, y, text, font, fillcolor, shadowcolor)
    output = BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=0.1)
    return output


async def make_qiegewala(texts):
    font = ImageFont.truetype('msyh.ttc', 20, encoding='utf-8')
    shadowcolor = (0, 0, 0)
    fillcolor = (255, 255, 255)

    frames = [Image.open(data_path / f'qiegewala/{i}.jpg')
              for i in range(0, 87)]
    parts = [frames[0:15], frames[16:31], frames[31:38],
             frames[38:48], frames[49:68], frames[68:86]]
    for part, text in zip(parts, texts):
        for frame in part:
            x, y = text_position(frame, text, font)
            if x < 5:
                return '文字长度过长，请适当缩减'
            draw = ImageDraw.Draw(frame)
            darw_text(draw, x, y, text, font, fillcolor, shadowcolor)
    output = BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=0.13)
    return output


async def make_luxunsay(texts):
    font = ImageFont.truetype('msyh.ttc', 38, encoding='utf-8')
    luxun_font = ImageFont.truetype('msyh.ttc', 30, encoding='utf-8')
    frame = Image.open(data_path / f'luxunsay/0.jpg')
    color = (255, 255, 255)

    text = texts[0]
    if len(text) > 40:
        return '文字长度过长，请适当缩减'
    x, y = text_position(frame, text, font, padding_y=130)
    if x < 25:
        n = math.ceil(len(text) / 2)
        text = text[:n] + '\n' + text[n:]
        x, y = text_position(frame, text[:n], font, padding_y=130)
        if x < 25:
            return '文字长度过长，请适当缩减'
    draw = ImageDraw.Draw(frame)
    draw.text((x, y), text, color, font)
    draw.text((320, 400), '--鲁迅', color, luxun_font)
    output = BytesIO()
    frame = frame.convert('RGBA')
    frame.save(output, format='png')
    return output


async def make_nokia(texts):

    def draw_lines(image, font, lines, gap, width, height, angle):
        new = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(new)
        for i, line in enumerate(lines):
            draw.text((0, i * gap), text=line, font=font, fill=(0, 0, 0, 255))
        new = new.rotate(angle, expand=True)
        px, py = (205, 330)
        w, h = new.size
        image.paste(new, (px, py, px + w, py + h), new)

    def draw_title(image, font, text, angle):
        new = Image.new('RGBA', font.getsize(text))
        draw = ImageDraw.Draw(new)
        draw.text((0, 0), text=text, font=font, fill=(129, 212, 250, 255))
        new = new.rotate(angle, expand=True)
        px, py = (790, 320)
        w, h = new.size
        image.paste(new, (px, py, px + w, py + h), new)

    text = texts[0][:900]
    frame = Image.open(data_path / f'nokia/0.jpg')
    font = ImageFont.truetype('方正像素14.ttf', 70, encoding='utf-8')
    lines = wrap_text(text, font, 700)[:5]
    draw_lines(frame, font, lines, 90, 700, 450, -9.3)
    draw_title(frame, font, f'{len(text)}/900', -9.3)
    output = BytesIO()
    frame = frame.convert('RGB')
    frame.save(output, format='jpeg')
    return output


async def make_goodnews(texts):
    font = ImageFont.truetype('msyh.ttc', 45, encoding='utf-8')
    lines = wrap_text(texts[0], font, 480)
    if len(lines) > 5:
        return '文字长度过长，请适当缩减'
    frame = Image.open(data_path / f'goodnews/0.jpg')
    new = Image.new('RGBA', frame.size)
    draw = ImageDraw.Draw(new)
    text_w = 0
    text_h = 0
    border = 3
    for i, line in enumerate(lines):
        text_h += 55
        text_w = max(text_w, font.getsize(line)[0] + border * 2)
        darw_text(draw, border, i * 55, line, font, (238, 0, 0), (255, 255, 153), border)
    img_w, img_h = frame.size
    x = int((img_w - text_w) / 2)
    y = int((img_h - text_h) / 2)
    frame.paste(new, (x, y), new)
    output = BytesIO()
    frame = frame.convert('RGBA')
    frame.save(output, format='png')
    return output


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
