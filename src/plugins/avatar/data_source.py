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
    avatar_url = 'http://q1.qlogo.cn/g?b=qq&nk={}&s=640'.format(user_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            result = await resp.read()
    md5 = hashlib.md5(result).hexdigest()
    if md5 == 'acef72340ac0e914090bd35799f5594e':
        avatar_url_small = 'http://q1.qlogo.cn/g?b=qq&nk={}&s=100'.format(user_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url_small) as resp:
                result = await resp.read()
    return Image.open(io.BytesIO(result)).convert('RGBA') if result else None


async def create_petpet(avatar):
    hand_frames = [image_path / f'petpet/frame{i}.png' for i in range(5)]
    hand_frames = [Image.open(i) for i in hand_frames]
    frame_locs = [(14, 20, 98, 98), (12, 33, 101, 85), (8, 40, 110, 76), (10, 33, 102, 84), (12, 20, 98, 98)]
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
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset), fill=255)
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
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    images = [i for i in (image_path / 'crawl').iterdir() if i.is_file()]
    crawl = Image.open(random.choice(images)).resize((500, 500), Image.ANTIALIAS)
    avatar = avatar.resize((100, 100), Image.ANTIALIAS)
    crawl.paste(avatar, (0, 400), mask=avatar)
    crawl = crawl.convert('RGB')
    output = io.BytesIO()
    crawl.save(output, format='jpeg')
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
    'support': create_support
}


async def get_image(user_id: str, type: str):
    try:
        if type in types:
            func = types[type]
            avatar = await get_avatar(user_id)
            if avatar:
                output = await func(avatar)
                if output:
                    return MessageSegment.image(f"base64://{base64.b64encode(output.getvalue()).decode()}")
        return None
    except (AttributeError, TypeError, OSError, ValueError):
        logger.debug(traceback.format_exc())
        return None
