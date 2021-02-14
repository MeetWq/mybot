import os
import random
from fuzzywuzzy import process
from nonebot.log import logger

dir_path = os.path.split(os.path.realpath(__file__))[0]


def get_image(keyword):
    img_dir_path = os.path.join(dir_path, 'images')
    images = os.listdir(img_dir_path)
    images = [os.path.splitext(i)[0] for i in images]
    name, score = process.extractOne(keyword, images)
    if score > 80:
        img_name = os.path.join(img_dir_path, name)
        img_ext = ['.jpg', '.png', '.gif']
        for ext in img_ext:
            img_path = img_name + ext
            if os.path.exists(img_path):
                return img_path
    return ''


def get_record(keyword):
    record_dir_path = os.path.join(dir_path, 'records')
    records = os.listdir(record_dir_path)
    records = [os.path.splitext(i)[0] for i in records]
    name, score = process.extractOne(keyword, records)
    if score > 60:
        record_name = os.path.join(record_dir_path, name)
        record_ext = ['.slk', '.mp3']
        for ext in record_ext:
            record_path = record_name + ext
            logger.debug(record_path)
            if os.path.exists(record_path):
                return record_path
    return ''


def get_words(keyword=''):
    img_dir_path = os.path.join(dir_path, 'cherry_words')
    images = os.listdir(img_dir_path)
    images = [os.path.splitext(i)[0] for i in images]
    if keyword:
        name, score = process.extractOne(keyword, images)
    else:
        random.shuffle(images)
        name = images[0]
    img_name = os.path.join(img_dir_path, name)
    img_ext = ['.jpg', '.png', '.gif']
    for ext in img_ext:
        img_path = img_name + ext
        if os.path.exists(img_path):
            return img_path
    return ''
