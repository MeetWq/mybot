import os
from PIL import Image, ImageFont, ImageDraw

dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

BG_COLOR = '#000000'
BOX_COLOR = '#F7971D'
LEFT_TEXT_COLOR = '#FFFFFF'
RIGHT_TEXT_COLOR = '#000000'


def create_left_img(text, font_size=100):
    font = ImageFont.truetype(os.path.join(dir_path, 'arial.ttf'), font_size)
    font_width, font_height = font.getsize(text)
    offset_font = font.font.getsize(text)[1][1]
    offset = int(font_height / 2)
    offset_right = int(font_width / len(text) * 0.25)
    img_height = font_height + offset_font + offset * 2
    img_width = font_width + offset_right

    img_size = img_width, img_height
    image = Image.new('RGBA', img_size, BG_COLOR)
    draw = ImageDraw.Draw(image)
    draw.text((0, offset), text, fill=LEFT_TEXT_COLOR, font=font)
    return image


def create_right_img(text, font_size=100):
    font = ImageFont.truetype(os.path.join(dir_path, 'arialbd.ttf'), font_size)
    font_width, font_height = font.getsize(text)
    offset_font = font.font.getsize(text)[1][1]
    offset = int(font_height / 4)
    offset_left = int(font_width / len(text) * 0.25)
    img_width = font_width + 2 * offset_left
    img_height = font_height + offset_font + offset * 2
    image = Image.new('RGBA', (img_width, img_height), BOX_COLOR)
    draw = ImageDraw.Draw(image)
    draw.text((offset_left, offset), text, fill=RIGHT_TEXT_COLOR, font=font)

    radii = 10
    magnify = 10
    radii = radii * magnify
    circle = Image.new('L', (radii * 2, radii * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)

    img_width_large = img_width * magnify
    img_height_large = img_height * magnify
    alpha = Image.new('L', (img_width_large, img_height_large), 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (img_width_large - radii, 0))
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (img_width_large - radii, img_height_large - radii))
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, img_height_large - radii))
    alpha = alpha.resize((img_width, img_height), Image.ANTIALIAS)
    image.putalpha(alpha)
    return image


async def create_logo(left_text, right_text):
    left_img = create_left_img(left_text)
    right_img = create_right_img(right_text)
    blank = 30
    bg_img_width = left_img.width + right_img.width + blank * 2
    bg_img_height = left_img.height
    bg_img = Image.new('RGBA', (bg_img_width, bg_img_height), BG_COLOR)
    bg_img.paste(left_img, (blank, 0))
    bg_img.paste(right_img, (blank + left_img.width, int((bg_img_height - right_img.height) / 2)), mask=right_img)
    output_path = os.path.join(cache_path, 'tmp.png')
    bg_img.save(output_path)
    return output_path
