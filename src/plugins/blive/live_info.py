import time
from nonebot.adapters.onebot.v11 import Message, MessageSegment


class LiveInfo():
    def __init__(self, info: dict):
        self.up_name = info['uname']
        self.status = info['live_status']
        self.time = time.strftime(
            "%y/%m/%d %H:%M:%S", time.localtime(info['live_time']))
        self.url = 'https://live.bilibili.com/' + str(info['room_id'])
        self.title = info['title']
        self.cover = info['cover_from_user']

    async def format_msg(self) -> Message:
        msg = None
        if self.status == 1:
            msg = Message()
            msg.append(
                f"{self.time}\n"
                f"{self.up_name} 开播啦！\n"
                f"{self.title}\n"
                f"直播间链接：{self.url}"
            )
            msg.append(MessageSegment.image(self.cover))
        elif self.status == 0:
            msg = f"{self.up_name} 下播了"
        elif self.status == 2:
            msg = f"{self.up_name} 下播了（轮播中）"
        return msg
