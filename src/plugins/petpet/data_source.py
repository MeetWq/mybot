import uuid
import aiohttp
import hashlib
import imageio
import traceback
from pathlib import Path
from PIL import Image as IMG
from nonebot.log import logger

dir_path = Path(__file__).parent
cache_path = Path('cache/petpet')
if not cache_path.exists():
    cache_path.mkdir(parents=True)


async def get_petpet(user_id):
    file_name = uuid.uuid1().hex
    avatar_path = cache_path / (file_name + '.jpg')
    petpet_path = cache_path / (file_name + '.gif')

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

    status = await create_petpet(avatar_path, petpet_path)
    if status:
        return str(petpet_path.absolute())
    return ''


async def create_petpet(input_path, output_path):
    try:
        avatar = IMG.open(input_path)
        hand_frames = [dir_path / f'frames/frame{i}.png' for i in range(5)]
        hand_frames = [IMG.open(i) for i in hand_frames]
        frame_locs = [(14, 20, 98, 98), (12, 33, 101, 85), (8, 40, 110, 76), (10, 33, 102, 84), (12, 20, 98, 98)]
        frames = []
        for i in range(5):
            frame = IMG.new('RGBA', (112, 112), (255, 255, 255, 0))
            x, y, l, w = frame_locs[i]
            avatar_resized = avatar.resize((l, w), IMG.ANTIALIAS)
            frame.paste(avatar_resized, (x, y))
            hand = hand_frames[i]
            frame.paste(hand, mask=hand)
            frames.append(frame)
        imageio.mimsave(output_path, frames, duration=0.06)
        return True
    except (AttributeError, TypeError, OSError):
        logger.debug(traceback.format_exc())
        return False
