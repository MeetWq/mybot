import random
import aiohttp
import hashlib
import imageio
import traceback
from pathlib import Path
from nonebot.log import logger
from PIL import Image, ImageDraw, ImageFilter

data_path = Path('src/data/emojis')
cache_path = Path('cache/avatar')
if not cache_path.exists():
    cache_path.mkdir(parents=True)


async def get_avatar(user_id, avatar_path):
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

    with avatar_path.open('wb') as f:
        f.write(result)
    return True


async def create_petpet(input_path, output_path):
    avatar = Image.open(input_path).convert('RGBA')
    hand_frames = [data_path / f'petpet/frame{i}.png' for i in range(5)]
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
    imageio.mimsave(output_path, frames, duration=0.06)
    return True


async def create_tear(input_path, output_path):
    avatar = Image.open(input_path).convert('RGBA')
    tear = Image.open(data_path / 'tear.png')
    frame = Image.new('RGBA', (1080, 804), (255, 255, 255, 0))
    left = avatar.resize((385, 385)).rotate(24, expand=True)
    right = avatar.resize((385, 385)).rotate(-11, expand=True)
    frame.paste(left, (-5, 355))
    frame.paste(right, (649, 310))
    frame.paste(tear, mask=tear)
    frame.save(output_path)
    return True


async def create_throw(input_path, output_path):
    avatar = Image.open(input_path).convert('RGBA')
    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 1
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    avatar = avatar.rotate(random.randint(1, 360), Image.BICUBIC)
    avatar = avatar.resize((143, 143), Image.ANTIALIAS)
    throw = Image.open(data_path / 'throw.png')
    throw.paste(avatar, (15, 178), mask=avatar)
    throw.save(output_path)
    return True


async def create_crawl(input_path, output_path):
    avatar = Image.open(input_path).convert('RGBA')
    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    offset = 1
    draw.ellipse((offset, offset, avatar.size[0] - offset, avatar.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0))
    avatar.putalpha(mask)
    images = [i for i in (data_path / 'crawl').iterdir() if i.is_file()]
    crawl = Image.open(random.choice(images)).resize((500, 500), Image.ANTIALIAS)
    avatar = avatar.resize((100, 100), Image.ANTIALIAS)
    crawl.paste(avatar, (0, 400), mask=avatar)
    crawl.save(output_path)
    return True


types = {
    'petpet': (create_petpet, '.gif'),
    'tear': (create_tear, '.png'),
    'throw': (create_throw, '.png'),
    'crawl': (create_crawl, '.png')
}


async def get_image(user_id: str, type: str):
    try:
        if type in types:
            func, img_ext = types[type]
            avatar_path = cache_path / f'{user_id}.jpg'
            img_path = cache_path / f'{user_id}_{type}{img_ext}'
            if await get_avatar(user_id, avatar_path):
                if await func(avatar_path, img_path):
                    return str(img_path.absolute())
    except (AttributeError, TypeError, OSError, ValueError):
        logger.debug(traceback.format_exc())
        return ''
