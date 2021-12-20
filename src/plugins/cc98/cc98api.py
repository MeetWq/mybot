import time
import httpx
import asyncio
from functools import wraps


class LoginError(Exception):
    pass


class NoContent(Exception):
    pass


class CC98_API_V2():

    def __init__(self, username, password, proxies=None):
        self.ENDPOINT = "https://api-v2.cc98.org/"
        self.s = httpx.AsyncClient(proxies=proxies)
        self.username = username
        self.password = password
        self.token = ""
        self.expiretime = -1

    def auth(func):
        """
        auth: 装饰器，如果登录状态已经过期会自动登录
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            self = args[0]
            if time.time() >= self.expiretime:
                try:
                    await self.login()
                except Exception as e:
                    raise LoginError(e)
            return await func(*args, **kwargs)
        return wrapper

    @auth
    async def ping(self):
        """
        尝试登录，返回True
        本函数可以用于lazyinit
        """
        return True

    async def fetch_real_real(self, url, trytimes=3):
        """
        给定url GET访问url 并返回json 包含自动重试机制
        不包含登录机制
        """
        x = await self.s.get(self.ENDPOINT + url, timeout=10)
        try:
            return x.json()
        except:
            statuscode = x.status_code
            if statuscode == 401:
                raise Exception("unauthorized")
            elif statuscode == 204:
                raise NoContent()
            if trytimes > 0:
                sleeptime = 3 + 5 * trytimes
                print(
                    "Error {statuscode} in url: {url}, sleep {sleeptime}s".format(**locals()))
                asyncio.sleep(sleeptime)
                return await self.fetch_real_real(url, trytimes - 1)
            else:
                raise

    @auth
    async def fetch_real(self, url):
        """
        包含登录 但没有缓存的fetch_real
        """
        return await self.fetch_real_real(url)

    async def fetch(self, url):
        """
        这个函数在子类中会被缓存，所以不应该加入@auth
        可以缓存的请求则调用fetch
        不应该缓存则调用fetch_real
        缓存没有命中时调用fetch_real才会真正登录
        """
        return await self.fetch_real(url)

    async def login(self):
        """
        发起登录请求 以获取access_token 存入self.token
        并将过期时间写入self.expiretime
        """
        print(f"Login! {self.username}")
        url = 'https://openid.cc98.org/connect/token'
        params = {
            'client_id': '9a1fd200-8687-44b1-4c20-08d50a96e5cd',
            'client_secret': '8b53f727-08e2-4509-8857-e34bf92b27f2',
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'scope': 'cc98-api openid'
        }
        x = await self.s.post(url, data=params)
        data = x.json()
        token = data["access_token"]
        expirein = data["expires_in"]
        self.token = token
        self.expiretime = int(time.time()) + expirein
        self.s.headers.update({"authorization": "Bearer " + self.token})

    async def topic_new(self, from_=0, size=20):
        """
        查看新帖 返回帖子的数组
        """
        return await self.fetch(f"topic/new?from={from_}&size={size}")

    async def board_topic(self, boardid, from_=0, size=20):
        """
        获取版面帖子列表
        """
        return await self.fetch(f"Board/{boardid}/topic?from={from_}&size={size}")

    async def topic_hot(self):
        """
        获取十大列表 返回十大帖子的数组
        """
        return await self.fetch("Topic/Hot")

    async def topic(self, id):
        """
        单个帖子 返回帖子
        """
        return await self.fetch(f"Topic/{id}")

    async def board(self, boardid):
        """
        单个板块 返回板块
        """
        return await self.fetch(f"board/{boardid}")

    async def topic_post(self, id, from_=0, size=20):
        """
        帖子的内容/回复 返回回复的数组
        """
        return await self.fetch(f"Topic/{id}/post?from={from_}&size={size}")

    async def topic_post_certain_user(self, id, userid, from_=0, size=20):
        """
        追踪用户的回复（如只看楼主） 返回回复的数组
        """
        return await self.fetch_real(
            f"Post/topic/user?topicid={id}&userid={userid}&from={from_}&size={size}")

    async def topic_post_certain_user_182(self, id, postid, from_=0, size=20):
        """
        心灵帖子的追踪用户的回复 返回回复的数组
        """
        return await self.fetch_real(
            f"Post/topic/anonymous/user?topicid={id}&postid={postid}&from={from_}&size={size}")

    @auth
    async def post_edit(self, id, content, title, contenttype=0, type=0, tag1=None, tag2=None, notifyPoster=None):
        """
        编辑一条回复
        """
        data = {"content": content, "contentType": contenttype,
                "title": title, "type": type}
        if tag1 and tag1 > 0:
            data["tag1"] = tag1
        if tag2 and tag2 > 0:
            data["tag2"] = tag2
        if notifyPoster is not None:
            data["notifyPoster"] = notifyPoster
        x = await self.s.put(self.ENDPOINT + f"post/{id}", json=data)
        status = x.status_code == 200
        if not status:
            print("[edit failed] ", x.text)
        return status

    @auth
    async def upload(self, fp, filename=None):
        """
        上传一张图片
        """
        if filename is None:
            filename = 'filename.gif'
        x = await self.s.post(self.ENDPOINT + "file?compressImage=false",
                              files=[('files', (filename, fp, 'image/jpeg')), ('contentType', 'multipart/form-data')])
        return x.json()

    @auth
    async def upload_portrait(self, fp):
        """
        上传一张头像
        """
        x = await self.s.post(self.ENDPOINT + "file/portrait",
                              files=[('files', ('头像.png', fp, 'image/png')), ('contentType', 'multipart/form-data')])
        return x.json()

    @auth
    async def signin(self, data="sign in!"):
        """
        签到
        """
        x = await self.s.post(self.ENDPOINT + "me/signin", data=data,
                              headers={"Content-Type": "application/json"})
        return x.status_code == 200

    @auth
    async def signin_status(self):
        """
        获取当前签到状态
        返回{"lastSignInTime":"2018-02-01T00:27:34.213","lastSignInCount":41,"hasSignedInToday":true}
        """
        try:
            return await self.fetch_real_real("me/signin")
        except NoContent:
            return {"lastSignInTime": None, "lastSignInCount": 0, "hasSignedInToday": False}

    @auth
    async def get_wealth(self):
        """
        获取当前财富值
        """
        return await self.fetch_real("me")["wealth"]

    async def userinfos(self, userids):
        """
        获取用户信息 输入userid的集合/数组，返回{userid: 用户信息}
        如果获取失败 转而获取用户的基本信息
        """
        try:
            data = await self.fetch_real(
                "user?id=" + "&id=".join([str(i) for i in userids]))
        except:
            data = await self.fetch_real(
                "user/basic?id=" + "&id=".join([str(i) for i in userids]))
        return {item["id"]: item for item in data}

    @auth
    async def get_user_topics(self, userid, _from=0, size=20):
        """
        获取用户最近的发帖
        """
        return await self.fetch_real(f"user/{userid}/recent-topic?from={_from}&size={size}")

    async def userinfobyname(self, username):
        """
        根据用户名获取用户信息
        """
        return await self.fetch("/User/Name/" + username)

    @auth
    async def topic_reply(self, id, content, title="", contenttype=0, parentId=0):
        data = {"content": content, "contentType": contenttype, "title": title}
        if parentId != 0:
            data["parentId"] = parentId
        x = await self.s.post(self.ENDPOINT + f"topic/{id}/post", json=data)
        ret = (x.status_code == 200)
        if not ret:
            print(x.status_code)
            print(x.text)
        return ret

    async def index(self):
        """
        返回首页的一些信息
        {
            'academics': 学术信息 boardId,id,state,title,state的list
            'announcement': 公告ubb字符串
            'emotion': 感性·情感
            'fleaMarket': 跳蚤市场
            'fullTimeJob': 求职广场
            'hotTopic': 十大 authorName boardId boardName createTime hitCount id participantCount replyCount title type
            'lastUpdateTime': 十大最后更新时间 如'2018-01-11T17:38:40.3985854+08:00'
            'lastUserName': 最新注册的用户名
            'partTimeJob': 实习兼职
            'postCount': 论坛总回复数
            'recommendationFunction': 推荐功能 imageUrl orderWeight title url
            'recommendationReading': 推荐阅读 content imageUrl orderWeight title url
            'schoolEvent': 校园活动
            'schoolNews': 校园新闻 time title url
            'study': 学习园地
            'todayCount': 今日帖数 如1284
            'topicCount': 主题数目 如1363166
            'userCount': 用户数目 如290913
        }
        该函数不需要登录
        """
        return await self.fetch_real_real("config/index")

    async def ads(self):
        """
        返回广告信息 数据结构为如下的数组
        {
            'expiredTime': '2018-12-31T16:46:59.3360354+08:00', # 过期时间
            'id': 37,
            'imageUrl': 'http://file.cc98.org/v2-upload/hozp3jrp.jpg', # 图片地址
            'url': '/topic/4687065' # 点击图片跳转到的url
        }
        """
        return await self.fetch_real_real("config/global/advertisement")

    @auth
    async def post_rating(self, postid, value, reason):
        """
        对回复进行评分，大于500帖的用户可以每天对一个帖子进行评分
        postid：回复id
        value: 1表示风评+1， -1表示减一
        reason: 理由 如"所言极是", "momo", "好人一生平安"; "太不求是", "呵呵", "被你暴击"
        返回评分是否成功 以及 返回的页面内容（在出错时可以显示给用户）
        """
        value = str(value)
        x = await self.s.put(self.ENDPOINT + f"post/{postid}/rating",
                             json={"value": {value}, "reason": {reason}})
        return x.status_code == 200, x.text

    async def board_all(self):
        """
        返回板块分类的数组 其数据结构为:
        {name: 分类名称 如"置顶", boards: 板块的数组, masters: 区务数组, order: 1}
        其中板块的数据结构为：{
            "id": 758,
            "name": "似水流年·寒假",
            "boardMasters": ["磊磊1010", "菰城碧", "笨蛋路路", "山峰的疯", "霏霏在此"],
            "description": "似水流年，畅所欲言。",
            "postCount": 3118307,
            "todayCount": 44,
        }
        """
        return await self.fetch("Board/all")

    async def board_all2(self):
        """
        如果不关心板块的分类，可以使用这个
        返回所有版块的dict {板块id: 板块信息}
        """
        result = {}
        parts = await self.board_all()
        for part in parts:
            result.update({b["id"]: b for b in part["boards"]})
        return result

    @auth
    async def post_reward(self, id, reason="好文章", wealth=1000):
        """
        对一条回复进行发米
        """
        x = await self.s.post(self.ENDPOINT + f"post/{id}/operation",
                              json={"operationType": 0, "reason": reason, "wealth": wealth})
        return x.status_code == 200

    @auth
    async def my_favorite(self, page=1):
        """
        返回收藏，第page页，每页20条
        本函数没有缓存， 需要登录状态不过已经有@auth了所以用fetch_real_real
        """
        from_ = (page - 1) * 20
        return await self.fetch_real_real(f"topic/me/favorite?from={from_}&size=20")

    @auth
    async def add_favorite(self, id):
        x = await self.s.put(self.ENDPOINT + f"me/favorite/{id}")
        return x.status_code == 200

    @auth
    async def remove_favorite(self, id):
        x = await self.s.delete(self.ENDPOINT + f"me/favorite/{id}")
        return x.status_code == 200

    @auth
    async def unread_count(self):
        return await self.fetch_real_real("me/unread-count")

    @auth
    async def new_topic(self, board, title, content, contentType=0, type=0, tag1=None, tag2=None, notifyPoster=True):
        """
        在board板块发新帖
        notifyPoster 是否接收回复的消息提醒 默认值为True接收
        返回新帖的topicid int类型，如4770672
        """
        data = {"content": content, "contentType": contentType,
                "title": title, "type": type, "notifyPoster": notifyPoster}
        if tag1 is not None:
            data["tag1"] = int(tag1)
        if tag2 is not None:
            data["tag2"] = int(tag2)
        url = self.ENDPOINT + f"board/{board}/topic"
        x = await self.s.post(url, json=data)
        if x.status_code != 200:
            raise Exception(x.text)
        return int(x.text)

    async def get_board_tag(self, boardid):
        """
        获取板块发帖所需要的标签
        返回两个数组 分别为tag1和tag2，每个数组内的元素为(tagid:int, name:str)
        例子：
        [(47, "内地"), (48, "国际")], []
        [(15, "问")], [(55, "实习")]
        """
        x = await self.fetch(f"/board/{boardid}/tag")
        result = {1: [], 2: []}
        for layer in x:
            for tag in layer["tags"]:
                result[layer["layer"]].append((tag["id"], tag["name"]))
        return result[1], result[2]

    @auth
    async def transfer_wealth(self, usernames, amount, reason):
        """
        对一些用户发起转账 向每个用户发送amount财富值
        但实际上对方只能收到min(amount*0.9, amount-10)财富值，例如想让对方收到1000则需要发送1111
        usernames: 用户名的数组
        wealth: int 每个用户发送多少
        reason: str 附言
        返回数组或错误字符串 如["username1", "username2"] 再如 "parameter_error"
        建议调用时将错误转为异常 assert isinstance(result, list), "transfer failed: "+result
        """
        x = await self.s.put(self.ENDPOINT + "me/transfer-wealth",
                             json={"userNames": usernames, "wealth": amount, "reason": reason})
        try:
            return x.json()
        except:
            return x.text

    @auth
    async def post_like(self, postid, action):
        """
        对帖子点赞action=="like"/点踩"dislike"
        返回{likeCount: 4, dislikeCount: 1, likeState: 2}
        """
        assert action in ["like", "dislike"]
        x = await self.s.put(self.ENDPOINT + f"post/{postid}/like", data="1" if action == "like" else "2")
        assert x.status_code == 200, "like PUT failed"
        x = await self.s.get(self.ENDPOINT + f"post/{postid}/like")
        return x.json()

    @auth
    async def get_followee_list(self, er="e"):
        """
        返回当前关注用户的用户id列表
        为了避免死循环，目前关注人数上限50，只需3次循环即可
        """
        from_ = 0
        result = []
        t = 0
        while len(result) == from_ and t < 50:
            x = await self.fetch_real_real(f"me/followe{er}?from={from_}&size=20")
            result.extend(x)
            from_ += 20
            t += 1
        return result

    async def get_follower_list(self):
        """
        返回粉丝用户id列表, 最多返回1000条
        """
        return self.get_followee_list(er="r")

    async def set_headpic(self, url):
        """
        设置当前用户头像url
        """
        if url.startswith("//"):
            url = "https:" + url
        x = await self.s.put(self.ENDPOINT + "me/portrait", data=f"{url}")
        return x.status_code == 200

    async def message_post(self, receiverId, content):
        """
        向receiverId用户发送私信 内容content
        返回是否成功，错误信息
        """
        id = int(receiverId)
        x = await self.s.post(self.ENDPOINT + "message", json={"receiverId": id, "content": content})
        return x.status_code == 200, x.text
