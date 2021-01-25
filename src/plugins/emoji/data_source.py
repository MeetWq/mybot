import os
import re
import random

dir_path = os.path.split(os.path.realpath(__file__))[0]


def get_emoji_path(name: str):
    patterns = [(r'ac\d{2,4}', 'ac'),
                (r'em\d{2}', 'em'),
                (r'[acf]:?\d{3}', 'mahjong'),
                (r'ms\d{2}', 'ms'),
                (r'tb\d{2}', 'tb')]
    name = name.strip().split('.')[0].replace(':', '')
    file_ext = ['.jpg', '.png', '.gif']
    for pattern, dir_name in patterns:
        if re.match(pattern, name):
            file_full_name = os.path.join(dir_path, 'images', dir_name, name)
            for ext in file_ext:
                file_path = file_full_name + ext
                if os.path.exists(file_path):
                    return file_path
    return None


def get_random_pic(name: str):
    dirs = {'cherry': 'cherry',
            'rabbit': 'rabbit',
            'ria': 'ria'}
    dir_name = dirs[name]
    dir_full_path = os.path.join(dir_path, 'images', dir_name)
    images = os.listdir(dir_full_path)
    random.shuffle(images)
    img_path = os.path.join(dir_full_path, images[0])
    return img_path
