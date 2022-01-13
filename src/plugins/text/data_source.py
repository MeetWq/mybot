import math
import random
from nonebot.log import logger

from .cxh import emoji, pinyin
from .hxw import enchars, encharhxw, ftw, hxw, jtw
from .flip import flip_table
from .bug import bug_code, bug_level


async def get_cxh_text(text: str):

    def get_pinyin(s):
        if s in pinyin:
            return pinyin[s]
        return ''

    result = ''
    for i in range(len(text)):
        pinyin1 = get_pinyin(text[i])
        pinyin2 = get_pinyin(text[i + 1]) if i < len(text) - 1 else ''
        if pinyin1 + pinyin2 in emoji:
            result += emoji[pinyin1 + pinyin2]
        elif pinyin1 in emoji:
            result += emoji[pinyin1]
        else:
            result += text[i]
    return result


async def get_hxw_text(text: str):
    result = ''
    for s in text:
        c = s
        if s in enchars:
            c = encharhxw[enchars.index(s)]
        elif s in jtw:
            c = hxw[jtw.index(s)]
        elif s in ftw:
            c = hxw[ftw.index(s)]
        result += c
    return result


async def get_ant_text(text: str):
    result = ''
    for s in text:
        result += s + chr(1161)
    return result


async def get_flip_text(text: str):
    text = text.lower()
    result = ''
    for s in text[::-1]:
        result += flip_table[s] if s in flip_table else s
    return result


async def get_bug_text(text: str):

    def bug(p, n):
        result = ''
        if isinstance(n, list):
            n = math.floor(random.random() * (n[1] - n[0] + 1)) + n[0]
        for i in range(n):
            result += bug_code[p][int(random.random() * len(bug_code[p]))]
        return result

    level = 12
    u = bug_level[level]
    result = ''
    for s in text:
        result += s
        if s != ' ':
            result += bug('mid', u['mid']) + \
                bug('above', u['above']) + \
                bug('under', u['under']) + \
                bug('up', u['up']) + \
                bug('down', u['down'])
    return result


commands = {
    'cxh': {
        'aliases': {'抽象话'},
        'func': get_cxh_text
    },
    'hxw': {
        'aliases': {'火星文'},
        'func': get_hxw_text
    },
    'ant': {
        'aliases': {'蚂蚁文'},
        'func': get_ant_text
    },
    'flip': {
        'aliases': {'翻转文字'},
        'func': get_flip_text
    },
    'bug': {
        'aliases': {'故障文字'},
        'func': get_bug_text
    }
}


async def get_text(type: str, text: str) -> str:
    try:
        func = commands[type]['func']
        return await func(text)
    except Exception as e:
        logger.warning(f"Error in get_text({text}, {type}): {e}")
        return ''
