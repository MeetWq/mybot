class Dynamic():
    def __init__(self, dynamic):
        self.dynamic = dynamic
        self.type = dynamic['desc']['type']
        self.id = dynamic['desc']['dynamic_id']
        self.url = "https://t.bilibili.com/" + str(self.id)
        self.time = dynamic['desc']['timestamp']
        self.uid = dynamic['desc']['user_profile']['info']['uid']
        self.name = dynamic['desc']['user_profile']['info'].get('uname')
