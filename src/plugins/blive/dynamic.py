from nonebot.adapters.cqhttp import Message, MessageSegment


class Dynamic():
    def __init__(self, dynamic):
        self.dynamic = dynamic
        self.type = dynamic['desc']['type']
        self.id = dynamic['desc']['dynamic_id']
        self.url = f"https://m.bilibili.com/dynamic/{self.id}"
        self.time = dynamic['desc']['timestamp']
        self.uid = dynamic['desc']['user_profile']['info']['uid']
        self.name = dynamic['desc']['user_profile']['info'].get('uname')

    def format_msg(self, img):
        type_msg = {
            0: "发布了新动态",
            1: "转发了一条动态",
            8: "发布了新投稿",
            16: "发布了短视频",
            64: "发布了新专栏",
            256: "发布了新音频"
        }
        msg = Message()
        msg.append(f"{self.name} {type_msg.get(self.type, type_msg[0])}:")
        msg.append(MessageSegment.image(img))
        return msg
