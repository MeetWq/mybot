import re
from nonebot import export, on_message
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent, MessageSegment

export = export()
export.description = '复读机'
export.usage = 'Usage:\n  重复两次的内容会被复读'
export.notice = 'Notice:\n  只能复读文本和图片；指令及其回复不会被复读'
export.help = export.description + '\n' + export.usage + '\n' + export.notice


async def repeat_rule(bot: Bot, event: Event, state: T_State) -> bool:
    return isinstance(event, GroupMessageEvent) and not event.to_me


repeat = on_message(rule=repeat_rule, priority=41, block=False)

msgs = {}


class Counter:
    def __init__(self):
        self.count = 0
        self.msg = None
        self.str_msg = ''

    def add_msg(self, msg):
        str_msg = str(msg)
        str_msg = re.sub(r',url=.*?]', ']', str_msg)
        if str_msg == '' or str_msg == '此处消息的转义尚未被插件支持' or '请使用最新版手机QQ体验新功能' in str_msg or re.fullmatch(r'&#91;[^:,= ]+&#93;', str_msg):
            self.count = 0
            self.str_msg = ''
        else:
            if str_msg == self.str_msg:
                self.count += 1
            else:
                if self.save_msg(msg):
                    self.count = 1
                    self.str_msg = str_msg
                else:
                    self.count = 0
                    self.str_msg = ''

    def save_msg(self, msg):
        easy_type = True
        for m in msg:
            if m.type not in ['text', 'face', 'at']:
                easy_type = False
        if easy_type:
            self.msg = msg
            return True
        elif len(msg) == 1:
            m = msg[0]
            if m.type == 'image':
                self.msg = MessageSegment.image(file=m.data['url'])
                return True
            elif m.type == 'record':
                self.msg = MessageSegment.record(file=m.data['url'])
                return True
        self.msg = None
        return False


@repeat.handle()
async def _(bot: Bot, event, state: T_State):
    if not isinstance(event, GroupMessageEvent):
        return
    msg = event.get_message()
    group_id = event.group_id
    if group_id not in msgs.keys():
        msgs[group_id] = Counter()
    msgs[group_id].add_msg(msg)
    if msgs[group_id].count == 2:
        msg = msgs[group_id].msg
        if msg:
            await repeat.finish(msg)
