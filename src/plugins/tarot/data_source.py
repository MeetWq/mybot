import json
import random
import numpy as np
from io import BytesIO
from typing import List
from pathlib import Path
from PIL.Image import Image as IMG
from PIL.ImageFont import FreeTypeFont
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from nonebot.log import logger

dir_path = Path(__file__).parent
tarot_path = dir_path / 'resources'
image_path = tarot_path / 'images'


async def get_tarot() -> BytesIO:
    type, card = get_random_tarot()
    reverse = random.choice([False, True])
    filename = '{}{:02d}.jpg'.format(type, card['num'])
    image = Image.open(image_path / filename)
    if reverse:
        image = image.rotate(180)
    content = f"{card['name']} ({card['name-en']}) {'逆位' if reverse else '正位'}\n" \
              f"牌意：{card['meaning']['reverse' if reverse else 'normal']}"

    try:
        img = make_tarot_tank(image, content)
    except Exception as e:
        logger.warning(f"Error in make_tarot_tank({content}): {e}")
        return None
    output = BytesIO()
    img.save(output, format='png')
    return output


def get_random_tarot():
    path = tarot_path / 'tarot.json'
    with path.open('r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    types = ['major', 'pentacles', 'wands', 'cups', 'swords']
    cards = []
    for type in types:
        cards.extend(data[type])
    card = random.choice(cards)
    for type in types:
        if card in data[type]:
            return type, card


def make_tarot_tank(img: IMG, content: str) -> IMG:
    font = ImageFont.truetype('msyh.ttc', 24, encoding='utf-8')
    lines = wrap_text(content, font, 430)[:4]
    text = '\n'.join(lines)
    text_w, text_h = font.getsize_multiline(text)
    frame = Image.new('RGB', (474, 1080), (0, 0, 0))
    frame.paste(img, (0, 0))
    x = 237 - int(text_w / 2)
    y = 1005 - int(text_h / 2)
    draw = ImageDraw.Draw(frame)
    draw.multiline_text((x, y), text, font=font, fill=(255, 255, 255))
    bg = Image.open(tarot_path / 'background.jpg')
    return color_car(bg, frame)


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


def color_car(wimg: IMG, bimg: IMG, wlight: float = 1.0, blight: float = 0.4,
              wcolor: float = 0.5, bcolor: float = 0.7, chess: bool = False) -> IMG:
    """
    发彩色车
    :param wimg: 白色背景下的图片
    :param bimg: 黑色背景下的图片
    :param wlight: wimg 的亮度
    :param blight: bimg 的亮度
    :param wcolor: wimg 的色彩保留比例
    :param bcolor: bimg 的色彩保留比例
    :param chess: 是否棋盘格化
    :return: 处理后的图像
    """
    wimg = ImageEnhance.Brightness(wimg).enhance(wlight)
    bimg = ImageEnhance.Brightness(bimg).enhance(blight)

    wpix = np.array(wimg).astype("float64")
    bpix = np.array(bimg).astype("float64")

    if chess:
        wpix[::2, ::2] = [255., 255., 255.]
        bpix[1::2, 1::2] = [0., 0., 0.]

    wpix /= 255.
    bpix /= 255.

    wgray = wpix[:, :, 0] * 0.334 + \
        wpix[:, :, 1] * 0.333 + wpix[:, :, 2] * 0.333
    wpix *= wcolor
    wpix[:, :, 0] += wgray * (1. - wcolor)
    wpix[:, :, 1] += wgray * (1. - wcolor)
    wpix[:, :, 2] += wgray * (1. - wcolor)

    bgray = bpix[:, :, 0] * 0.334 + \
        bpix[:, :, 1] * 0.333 + bpix[:, :, 2] * 0.333
    bpix *= bcolor
    bpix[:, :, 0] += bgray * (1. - bcolor)
    bpix[:, :, 1] += bgray * (1. - bcolor)
    bpix[:, :, 2] += bgray * (1. - bcolor)

    d = 1. - wpix + bpix

    d[:, :, 0] = d[:, :, 1] = d[:, :, 2] = \
        d[:, :, 0] * 0.222 + d[:, :, 1] * 0.707 + d[:, :, 2] * 0.071

    p = np.where(d != 0, bpix / d * 255., 255.)
    a = d[:, :, 0] * 255.

    colors = np.zeros((p.shape[0], p.shape[1], 4))
    colors[:, :, :3] = p
    colors[:, :, -1] = a

    colors[colors > 255] = 255

    return Image.fromarray(colors.astype("uint8")).convert("RGBA")
