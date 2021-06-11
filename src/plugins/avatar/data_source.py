import io
import base64
import random
import aiohttp
import hashlib
import imageio
import traceback
from pathlib import Path
from nonebot.log import logger
from PIL import Image, ImageDraw, ImageFilter
from nonebot.adapters.cqhttp import MessageSegment

dir_path = Path(__file__).parent
image_path = dir_path / 'images'


async def get_avatar(user_id):
    result = None
    avatar_url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            result = await resp.read()
    md5 = hashlib.md5(result).hexdigest()
    if md5 == 'acef72340ac0e914090bd35799f5594e':
        avatar_url_small = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url_small) as resp:
                result = await resp.read()
    return Image.open(io.BytesIO(result)).convert('RGBA') if result else None


async def get_img(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as resp:
            result = await resp.read()
    if not result:
        return None
    img = Image.open(io.BytesIO(result))
    img = await crop_square(img)
    return img.convert('RGBA')


async def crop_square(img):
    width, height = img.size
    length = min(width, height)
    return img.crop(((width - length) / 2, (height - length) / 2,
                     (width + length) / 2, (height + length) / 2))


async def create_petpet(avatar):
    hand_frames = [image_path / f'petpet/frame{i}.png' for i in range(5)]
    hand_frames = [Image.open(i) for i in hand_frames]
    frame_locs = [(14, 20, 98, 98), (12, 33, 101, 85),
                  (8, 40, 110, 76), (10, 33, 102, 84), (12, 20, 98, 98)]
    frames = []
    for i in range(5):
        frame = Image.new('RGBA', (112, 112), (255, 255, 255, 0))
        x, y, l, w = frame_locs[i]
        avatar_resized = avatar.resize((l, w), Image.ANTIALIAS)
        frame.paste(avatar_resized, (x, y))
        hand = hand_frames[i]
        frame.paste(hand, mask=hand)
        frames.append(frame)
    output = io.BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=0.06)
    return output


async def create_tear(avatar):
    tear = Image.open(image_path / 'tear.png')
    frame = Image.new('RGBA', (1080, 804), (255, 255, 255, 0))
    left = avatar.resize((385, 385)).rotate(24, expand=True)
    right = avatar.resize((385, 385)).rotate(-11, expand=True)
    frame.paste(left, (-5, 355))
    frame.paste(right, (649, 310))
    frame.paste(tear, mask=tear)
    frame = frame.convert('RGB')
    output = io.BytesIO()
    frame.save(output, format='jpeg')
    return output


async def create_throw(avatar):
    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 1
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset),
                 fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    avatar = avatar.rotate(random.randint(1, 360), Image.BICUBIC)
    avatar = avatar.resize((143, 143), Image.ANTIALIAS)
    throw = Image.open(image_path / 'throw.png')
    throw.paste(avatar, (15, 178), mask=avatar)
    throw = throw.convert('RGB')
    output = io.BytesIO()
    throw.save(output, format='jpeg')
    return output


async def create_crawl(avatar):
    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 1
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset),
                 fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    images = [i for i in (image_path / 'crawl').iterdir() if i.is_file()]
    crawl = Image.open(random.choice(images)).resize(
        (500, 500), Image.ANTIALIAS)
    avatar = avatar.resize((100, 100), Image.ANTIALIAS)
    crawl.paste(avatar, (0, 400), mask=avatar)
    crawl = crawl.convert('RGB')
    output = io.BytesIO()
    crawl.save(output, format='jpeg')
    return output


async def resize_img(img, width, height, angle=0):
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    img.putalpha(mask)
    img = img.resize((width, height), Image.ANTIALIAS)
    if angle:
        img = img.rotate(angle, Image.BICUBIC, expand=True)
    return img


async def create_kiss(self_img, user_img):
    user_locs = [(92, 64), (135, 40), (84, 105), (80, 110), (155, 82), (60, 96),
                 (50, 80), (98, 55), (35, 65), (38, 100), (70, 80), (84, 65), (75, 65)]
    self_locs = [(58, 90), (62, 95), (42, 100), (50, 100), (56, 100), (18, 120),
                 (28, 110), (54, 100), (46, 100), (60, 100), (35, 115), (20, 120), (40, 96)]
    frames = []
    for i in range(13):
        frame = Image.open(image_path / f'kiss/frame{i}.png').convert('RGBA')
        user_img_new = await resize_img(user_img, 50, 50)
        x, y = user_locs[i]
        frame.paste(user_img_new, (x, y), mask=user_img_new)
        self_img_new = await resize_img(self_img, 40, 40)
        x, y = self_locs[i]
        frame.paste(self_img_new, (x, y), mask=self_img_new)
        frames.append(frame)
    output = io.BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=0.05)
    return output


async def create_rub(self_img, user_img):
    user_locs = [(39, 91, 75, 75, 0), (49, 101, 75, 75, 0), (67, 98, 75, 75, 0),
                 (55, 86, 75, 75, 0), (61, 109, 75, 75, 0), (65, 101, 75, 75, 0)]
    self_locs = [(102, 95, 70, 80, 0), (108, 60, 50, 100, 0), (97, 18, 65, 95, 0),
                 (65, 5, 75, 75, -20), (95, 57, 100, 55, -70), (109, 107, 65, 75, 0)]
    frames = []
    for i in range(6):
        frame = Image.open(image_path / f'rub/frame{i}.png').convert('RGBA')
        x, y, w, h, angle = user_locs[i]
        user_img_new = await resize_img(user_img, w, h, angle)
        frame.paste(user_img_new, (x, y), mask=user_img_new)
        x, y, w, h, angle = self_locs[i]
        self_img_new = await resize_img(self_img, w, h, angle)
        frame.paste(self_img_new, (x, y), mask=self_img_new)
        frames.append(frame)
    output = io.BytesIO()
    imageio.mimsave(output, frames, format='gif', duration=0.05)
    return output


async def create_support(avatar):
    support = Image.open(image_path / 'support.png')
    frame = Image.new('RGBA', (1293, 1164), (255, 255, 255, 0))
    avatar = avatar.resize((815, 815), Image.ANTIALIAS).rotate(23, expand=True)
    frame.paste(avatar, (-172, -17))
    frame.paste(support, mask=support)
    frame = frame.convert('RGB')
    output = io.BytesIO()
    frame.save(output, format='jpeg')
    return output


types = {
    'petpet': create_petpet,
    'tear': create_tear,
    'throw': create_throw,
    'crawl': create_crawl,
    'kiss': create_kiss,
    'rub': create_rub,
    'support': create_support
}


async def get_image(type: str, self_id: str, user_id: str = '', img_url: str = ''):
    try:
        if type not in types:
            return None

        func = types[type]
        if user_id:
            user_img = await get_avatar(user_id)
        elif img_url:
            user_img = await get_img(img_url)
        else:
            return None

        if not user_img:
            return None

        if type in ['rub', 'kiss']:
            self_img = await get_avatar(self_id)
            if not self_img:
                return None
            output = await func(self_img, user_img)
        else:
            output = await func(user_img)
        if output:
            return MessageSegment.image(f"base64://{base64.b64encode(output.getvalue()).decode()}")
        return None
    except (AttributeError, TypeError, OSError, ValueError):
        logger.debug(traceback.format_exc())
        return None
