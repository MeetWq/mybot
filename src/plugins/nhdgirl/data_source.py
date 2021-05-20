import re
import json
import random
from pathlib import Path
from nonebot.adapters.cqhttp import Message, MessageSegment

dir_path = Path(__file__).parent
words_path = dir_path / 'words.json'


async def get_response(msg, nickname):
    reply = await get_reply(msg)
    if reply:
        reply = format_reply(reply, nickname)
        return reply
    return None


async def get_reply(msg):
    words = json.load(words_path.open('r', encoding='utf-8'))['words']
    for word in words:
        for s in word['msg']:
            if s in msg:
                return random.choice(word['reply'])


def format_reply(reply, nickname):
    reply = re.sub(r'\[/nickname\]', nickname, reply)
    p_at = r'(\[/at \d+\])'
    p_at_qq = r'\[/at (\d+)\]'
    replies = re.split(p_at, reply)
    reply = Message()
    for r in replies:
        match = re.match(p_at_qq, r)
        if match:
            reply.append(MessageSegment.at(match.group(1)))
        else:
            reply.append(r)
    return reply
