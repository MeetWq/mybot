import re
from typing import Dict
from nonebot import on_message, get_driver
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent, Message, MessageSegment, unescape

from .config import Config
global_config = get_driver().config
repeat_config = Config(**global_config.dict())


__des__ = '复读机'
__cmd__ = '''
重复两次的内容会被复读；只能复读文本和图片；指令及其回复不会被复读
'''.strip()
__short_cmd__ = '无'
__usage__ = f'{__des__}\nUsage:\n{__cmd__}'


class Counter:
    def __init__(self):
        self.count = 0
        self.msg = None

    def clear(self):
        self.count = 0
        self.msg = None

    def add_msg(self, msg: Message):
        for m in msg:
            if m.type not in ['text', 'face', 'at', 'image']:
                self.clear()
                return
            if m.type == 'text':
                m.data['text'] = unescape(m.data['text'])

        if self.compare_msg(msg):
            self.count += 1
            self.msg = msg
        else:
            self.count = 1
            self.msg = msg

    def compare_msg(self, msg: Message):
        if not self.msg:
            return True
        if len(self.msg) != len(msg):
            return False
        for m1, m2 in zip(self.msg, msg):
            if m1.type != m2.type:
                return False
            if not self.compare_msgseg(m1, m2):
                return False
        return True

    def compare_msgseg(self, msg1: MessageSegment, msg2: MessageSegment):
        msg_type = msg1.type
        if msg_type == 'text':
            text = msg2.data['text']
            if not text \
                or '此处消息的转义尚未被插件支持' in text \
                or '请使用最新版手机QQ体验新功能' in text \
                or re.fullmatch(r'\[\S+\]', text):
                return False
            return msg1.data['text'] == msg2.data['text']
        elif msg_type == 'face':
            return msg1.data['id'] == msg2.data['id']
        elif msg_type == 'at':
            return msg1.data['qq'] == msg2.data['qq']
        elif msg_type == 'image':
            return msg1.data['file'] == msg2.data['file']


async def repeat_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupMessageEvent) and not event.to_me


msgs: Dict[int, Counter] = {}
repeat = on_message(rule=repeat_rule, priority=41, block=False)


@repeat.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    msg = event.get_message()
    if not msg:
        await repeat.finish()

    group_id = event.group_id
    if group_id not in msgs.keys():
        msgs[group_id] = Counter()
    counter = msgs[group_id]

    if event.reply:
        counter.clear()
    else:
        counter.add_msg(msg)

    if counter.count == repeat_config.repeat_count:
        msg = counter.msg
        if msg:
            await repeat.finish(msg)
