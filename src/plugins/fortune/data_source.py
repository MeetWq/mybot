import os
import json
import random
from datetime import datetime
from nonebot.adapters.cqhttp import Message, MessageSegment

dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)


async def get_response(group_id, user_id):
    date = datetime.now().strftime('%Y%m%d')
    log_path = os.path.join(cache_path, date + '_' + str(group_id) + '.log')
    if not os.path.exists(log_path):
        with open(log_path, 'w') as f:
            pass
    with open(log_path, 'r+') as f:
        logs = f.readlines()
        logs = [l.strip() for l in logs]
        print(logs)
        if str(user_id) not in logs:
            f.write(str(user_id) + '\n')
            copywriting = get_copywriting()
            luck = copywriting['luck']
            content = copywriting['content']
            type = get_type(luck)
            face = get_face(luck)
            message = Message()
            message.append(f'\n运势: {type}\n{content}\n')
            message.append(MessageSegment.image(file='file://' + face))
            return message
        else:
            return '你今天已经抽过签了，请明天再来~'


def get_copywriting():
    path = os.path.join(dir_path, 'copywriting.json')
    with open(path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return random.choice(data['copywriting'])


def get_type(luck):
    path = os.path.join(dir_path, 'types.json')
    with open(path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    types = data['types']
    for type in types:
        if luck == type['luck']:
            return type['name']


def get_face(luck):
    path = os.path.join(dir_path, 'face')
    if luck in [10, 26]:
        face_id = '04'
    elif luck in [9, 20]:
        face_id = '05'
    elif luck in [8, 21, 22]:
        face_id = '02'
    elif luck in [7, 27]:
        face_id = '09'
    elif luck in [6, 24]:
        face_id = '06'
    elif luck in [5, 25]:
        face_id = '07'
    elif luck in [4, 23]:
        face_id = '10'
    elif luck in [-6]:
        face_id = '03'
    elif luck in [-7]:
        face_id = '01'
    elif luck in [-8]:
        face_id = '11'
    elif luck in [-9]:
        face_id = '08'
    elif luck in [-10]:
        face_id = '12'
    return os.path.join(path, face_id + '.png')
