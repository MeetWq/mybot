import json
import random
from pathlib import Path
from nonebot.adapters.cqhttp import Message, MessageSegment
from nonebot.log import logger

dir_path = Path(__file__).parent
tarot_path = dir_path / 'tarot'


async def get_tarot():
    card, filename = get_random_tarot()
    logger.debug(filename)
    dir = random.choice(['normal', 'reverse'])
    type = '正位' if dir == 'normal' else '逆位'
    content = f"{card['name']} ({card['name-en']}) {type}\n牌意：{card['meaning'][dir]}"

    msg = Message()
    img_path = tarot_path / dir / (filename + '.jpg')
    logger.debug(str(img_path))
    if filename and img_path.exists():
        msg.append(MessageSegment.image(file='file://' + str(img_path.absolute())))
    msg.append(MessageSegment.text(content))
    return msg


def get_random_tarot():
    path = tarot_path / 'tarot.json'
    with path.open('r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    kinds = ['major', 'pentacles', 'wands', 'cups', 'swords']
    cards = []
    for kind in kinds:
        cards.extend(data[kind])
    card = random.choice(cards)
    filename = ''
    for kind in kinds:
        if card in data[kind]:
            filename = '{}{:02d}'.format(kind, card['num'])
            break
    return card, filename
