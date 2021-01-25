import requests
import json
import time
import pickle
import random
from time import sleep
from functools import wraps
from urllib.parse import quote

try:
    from config_cc98api import SHOULD_RETRY, CALLBACKS

    """
    为了支持如网站访问统计等特定场景，你可以指定config_cc98api.py
    SHOULD_RETRY: 遇到调用出错时是否重试，如果用户在等待(用于网站后端)则应该设置为False 将立即抛出异常，默认为True
    CALLBACKS: 回调函数簇 默认为空
        目前存在的回调函数：
            CALLBACKS["apifetch"] 在fetch_real_real中调用， 可以用于统计调用次数
        如果CALLBACKS中没有需要的函数，调用下述的DUMMY_FUNC；
        调用规定：传入locals()，返回值不管；也不处理其异常，如果需要中断处理过程 可以抛出异常
    """
except:
    SHOULD_RETRY = True
    CALLBACKS = {}
try:
    from config import PROXY_OVERRIDE
except:
    PROXY_OVERRIDE = []
try:
    from config import PROXY_NOPROXY
except:
    PROXY_NOPROXY = False

DUMMY_FUNC = lambda variables: True


class LoginError(Exception):
    pass


class NoContent(Exception):
    pass


def auth(func):
    """
    auth: 装饰器，如果登录状态已经过期会自动登录
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        if time.time() >= self.expiretime:
            try:
                self.login()
            except Exception as e:
                raise LoginError(e)
        return func(*args, **kwargs)

    return wrapper


class CC98_API_V2():
    ENDPOINT = "https://api-v2.cc98.org/"

    """
    __init__(username, password, proxy=None): 构造函数需要传入用户名和密码 还可以传入一个proxy的数组 在403时随机选择代理进行访问 现在构造函数不会自动登录
    fetch(url): 给定url 使用登录状态GET访问url 并返回json
        fetch_real(url): 当不想被缓存的时候用这个 会使用登录状态
        fetch_real_real(url): 无需登录的请求用这个 不会触发登录
    login(): 发起登录请求 更新请求使用的access_token
    topic_new(from_=0, size=20): 查看新帖 返回帖子的数组
    board_topic(boardid, from_=0, size=20): 获取版面帖子列表 返回帖子的数组
    topic_hot(): 获取十大列表 返回十大帖子的数组
    topic(id): 单个帖子 返回帖子
    board(boardid): 单个板块 返回板块
    topic_post(id): 帖子的内容/回复 返回回复的数组
    post_edit(id, content, title, contenttype=0, type=0): 编辑一条回复
    upload(fp, filename=None): 上传一张图片
    upload_portrait(fp): 上传一张头像
    signin(data="sign in!"): 签到
    signin_status(): 获取当前签到状态
    get_wealth(): 获取当前财富值
    userinfos(userids): 获取用户信息 输入userid的集合/数组，返回{userid: 用户信息}
    get_user_topics(self, userid, _from=0, size=20): 获取用户最近的发帖
    userinfobyname(username): 根据用户名获取用户信息
    topic_reply(id, content, title="", contenttype=0): 对帖子进行回复
    index(): 返回首页显示的信息
    ads(): 返回广告的数组
    board_all(): 返回板块分类的数组 包含所有板块的基本信息
        board_all2(): 返回所有版块的dict，不包含分类信息
    post_reward(id, reason="好文章", wealth=1000): 对回复发米
    my_favorite(page=1): 返回收藏，第page页，每页20条
    add_favorite(id): 添加收藏，返回True或False
    remove_favorite(id): 移除收藏，返回True或False
    unread_count(): 查询未读通知数量，返回{"replyCount":0, "atCount":0, "systemCount":0, "messageCount":0}
    new_topic(board, title, content, contentType=0, type=0): 在board板块发新帖
    """

    def __init__(self, username, password, proxy=None):
        self.s = requests.session()
        self.username = username
        self.password = password
        if proxy:
            self.proxy = proxy
        else:
            self.proxy = []
        self.token = ""
        self.expiretime = -1  # no login at __init__

    @auth
    def ping(self):
        # 尝试登录，返回True
        # 本函数可以用于lazyinit
        return True

    def fetch_real_real(self, url, trytimes=0):
        """
        给定url GET访问url 并返回json 包含自动重试机制
        不包含登录机制
        """
        if len(PROXY_OVERRIDE):
            p = random.choice(PROXY_OVERRIDE)
            self.s.proxies = {"https": p}
        if PROXY_NOPROXY:
            self.s.proxies = {}
        x = self.s.get(self.ENDPOINT + url)
        CALLBACKS.get("apifetch", DUMMY_FUNC)(locals())
        try:
            return x.json()
        except:
            sleeptime = 3 + 5 * trytimes
            statuscode = x.status_code
            if statuscode == 401:
                raise Exception("unauthorized")
            elif statuscode == 204:
                raise NoContent()
            if SHOULD_RETRY:
                if trytimes > 5:
                    raise
                else:
                    print("Error {statuscode} in url: {url}, sleep {sleeptime}s".format(**locals()))
                    sleep(sleeptime)
                    if statuscode == 403 and trytimes > 0 and self.proxy is not None and len(self.proxy):
                        newproxy = random.choice(self.proxy)
                        print("Change proxy to " + newproxy)
                        self.s.proxies = {"https": newproxy}
                    return self.fetch_real_real(url, trytimes + 1)
            else:
                raise  # 如果SHOULD_RETRY为False, 只要遇到错误就抛出 不进行重试

    @auth
    def fetch_real(self, url):
        """
        包含登录 但没有缓存的fetch_real
        """
        return self.fetch_real_real(url)

    def fetch(self, url):
        """
        这个函数在子类中会被缓存，所以不应该加入@auth
        可以缓存的请求则调用fetch
        不应该缓存则调用fetch_real
        缓存没有命中时调用fetch_real才会真正登录
        """
        return self.fetch_real(url)

    def login(self):
        """
        发起登录请求 以获取access_token 存入self.token
        并将过期时间写入self.expiretime
        """
        print("Login! " + self.username)
        x = self.s.post("https://openid.cc98.org/connect/token",
                        "client_id=9a1fd200-8687-44b1-4c20-08d50a96e5cd&client_secret=8b53f727-08e2-4509-8857-e34bf92b27f2&grant_type=password&username={username}&password={password}&scope=cc98-api%20openid".format(
                            username=quote(self.username), password=quote(self.password)),
                        headers={"content-type": "application/x-www-form-urlencoded"})
        data = x.json()
        token = data["access_token"]
        expirein = data["expires_in"]
        self.token = token
        self.expiretime = int(time.time()) + expirein
        self.s.headers.update({"authorization": "Bearer " + self.token})

    # 查看新帖 返回帖子的数组
    def topic_new(self, from_=0, size=20):
        return self.fetch("topic/new?from={from_}&size={size}".format(**locals()))

    # 获取版面帖子列表
    def board_topic(self, boardid, from_=0, size=20):
        return self.fetch("Board/{boardid}/topic?from={from_}&size={size}".format(**locals()))

    # 获取十大列表 返回十大帖子的数组
    topic_hot = lambda self: self.fetch("Topic/Hot")

    # 单个帖子 返回帖子
    topic = lambda self, id: self.fetch("Topic/" + str(id))

    # 单个板块 返回板块
    board = lambda self, boardid: self.fetch("board/" + str(boardid))

    # 帖子的内容/回复 返回回复的数组
    def topic_post(self, id, from_=0, size=20):
        return self.fetch("Topic/{id}/post?from={from_}&size={size}".format(**locals()))

    # 追踪用户的回复（如只看楼主） 返回回复的数组
    def topic_post_certain_user(self, id, userid, from_=0, size=20):
        return self.fetch_real(
            "Post/topic/user?topicid={id}&userid={userid}&from={from_}&size={size}".format(**locals()))

    # 心灵帖子的追踪用户的回复 返回回复的数组
    def topic_post_certain_user_182(self, id, postid, from_=0, size=20):
        return self.fetch_real(
            "Post/topic/anonymous/user?topicid={id}&postid={postid}&from={from_}&size={size}".format(**locals()))

    # 编辑一条回复
    @auth
    def post_edit(self, id, content, title, contenttype=0, type=0, tag1=None, tag2=None, notifyPoster=None):
        data = {"content": content, "contentType": contenttype, "title": title, "type": type}
        if tag1 and tag1 > 0:
            data["tag1"] = tag1
        if tag2 and tag2 > 0:
            data["tag2"] = tag2
        if notifyPoster is not None:
            data["notifyPoster"] = notifyPoster
        x = self.s.put(self.ENDPOINT + "post/" + str(id), json.dumps(data),
                       headers={"content-type": "application/json"})
        status = x.status_code == 200
        if not status:
            print("[edit failed] ", x.text)
        return status

    # 上传一张图片
    @auth
    def upload(self, fp, filename=None):
        if filename is None:
            filename = 'filename.gif'
        x = self.s.post(self.ENDPOINT + "file?compressImage=false",
                        files=[('files', (filename, fp, 'image/jpeg')), ('contentType', 'multipart/form-data')])
        return x.json()

    # 上传一张头像
    @auth
    def upload_portrait(self, fp):
        x = self.s.post(self.ENDPOINT + "file/portrait",
                        files=[('files', ('头像.png', fp, 'image/png')), ('contentType', 'multipart/form-data')])
        return x.json()

    # 签到
    @auth
    def signin(self, data="sign in!"):
        x = self.s.post(self.ENDPOINT + "me/signin", data=data, headers={"Content-Type": "application/json"})
        return x.status_code == 200

    # 获取当前签到状态
    # 返回{"lastSignInTime":"2018-02-01T00:27:34.213","lastSignInCount":41,"hasSignedInToday":true}
    @auth
    def signin_status(self):
        try:
            return self.fetch_real_real("me/signin")
        except NoContent:
            return {"lastSignInTime": None, "lastSignInCount": 0, "hasSignedInToday": False}

    # 获取当前财富值
    @auth
    def get_wealth(self):
        return self.fetch_real("me")["wealth"]  # this function should not be cached

    # 获取用户信息 输入userid的集合/数组，返回{userid: 用户信息}
    def userinfos(self, userids):
        # no cache for this fetch now
        # 如果获取失败 转而获取用户的基本信息
        try:
            data = self.fetch_real("user?id=" + "&id=".join([str(i) for i in userids]))
        except:
            data = self.fetch_real("user/basic?id=" + "&id=".join([str(i) for i in userids]))
        return {item["id"]: item for item in data}

    # 获取用户最近的发帖
    @auth
    def get_user_topics(self, userid, _from=0, size=20):
        return self.fetch_real("user/{userid}/recent-topic?from={_from}&size={size}".format(**locals()))

    # 根据用户名获取用户信息
    def userinfobyname(self, username):
        return self.fetch("/User/Name/" + username)

    @auth
    def topic_reply(self, id, content, title="", contenttype=0, parentId=0):
        data = {"content": content, "contentType": contenttype, "title": title}
        if parentId != 0:
            data["parentId"] = parentId
        x = self.s.post(self.ENDPOINT + "topic/{id}/post".format(**locals()), json.dumps(data),
                        headers={"content-type": "application/json"})
        ret = (x.status_code == 200)
        if not ret:
            print(x.status_code)
            print(x.text)
        return ret

    def index(self):
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
        return self.fetch_real_real("config/index")

    def ads(self):
        """
        返回广告信息 数据结构为如下的数组
        {
            'expiredTime': '2018-12-31T16:46:59.3360354+08:00', # 过期时间
            'id': 37,
            'imageUrl': 'http://file.cc98.org/v2-upload/hozp3jrp.jpg', # 图片地址
            'url': '/topic/4687065' # 点击图片跳转到的url
        }
        """
        return self.fetch_real_real("config/global/advertisement")

    @auth
    def post_rating(self, postid, value, reason):
        """
        对回复进行评分，大于500帖的用户可以每天对一个帖子进行评分
        postid：回复id
        value: 1表示风评+1， -1表示减一
        reason: 理由 如"所言极是", "momo", "好人一生平安"; "太不求是", "呵呵", "被你暴击"

        返回评分是否成功 以及 返回的页面内容（在出错时可以显示给用户）
        """
        value = str(value)
        x = self.s.put(self.ENDPOINT + "post/{postid}/rating".format(**locals()),
                       ("""{"value":%s,"reason":"%s"}""" % (value, reason)).encode("utf-8"),
                       headers={"Content-Type": "application/json"})
        return x.status_code == 200, x.text

    def board_all(self):
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
        return self.fetch("Board/all")

    def board_all2(self):
        """
        如果不关心板块的分类，可以使用这个
        返回所有版块的dict {板块id: 板块信息}
        """
        result = {}
        for part in self.board_all():
            result.update({b["id"]: b for b in part["boards"]})
        return result

    # 对一条回复进行发米
    @auth
    def post_reward(self, id, reason="好文章", wealth=1000):
        x = self.s.post(self.ENDPOINT + "post/" + str(id) + "/operation",
                        json.dumps({"operationType": 0, "reason": reason, "wealth": wealth}),
                        headers={"content-type": "application/json"})
        return x.status_code == 200

    @auth
    def my_favorite(self, page=1):
        """
        返回收藏，第page页，每页20条
        本函数没有缓存， 需要登录状态不过已经有@auth了所以用fetch_real_real
        """
        from_ = (page - 1) * 20
        return self.fetch_real_real("topic/me/favorite?from={from_}&size=20".format(**locals()))

    @auth
    def add_favorite(self, id):
        x = self.s.put(self.ENDPOINT + "me/favorite/" + str(id))
        return x.status_code == 200

    @auth
    def remove_favorite(self, id):
        x = self.s.delete(self.ENDPOINT + "me/favorite/" + str(id))
        return x.status_code == 200

    @auth
    def unread_count(self):
        return self.fetch_real_real("me/unread-count")

    @auth
    def new_topic(self, board, title, content, contentType=0, type=0, tag1=None, tag2=None, notifyPoster=True):
        """
        在board板块发新帖
        notifyPoster 是否接收回复的消息提醒 默认值为True接收
        返回新帖的topicid int类型，如4770672
        """
        assert isinstance(notifyPoster, bool), "notifyPoster should be True or False"
        data = {"content": content, "contentType": int(contentType), "title": title, "type": int(type),
                "notifyPoster": notifyPoster}
        if tag1 is not None:
            data["tag1"] = int(tag1)
        if tag2 is not None:
            data["tag2"] = int(tag2)
        url = self.ENDPOINT + "board/{board}/topic".format(**locals())
        x = self.s.post(url, json.dumps(data), headers={"content-type": "application/json"})
        if x.status_code != 200:
            raise Exception(x.text)
        return int(x.text)

    def get_board_tag(self, boardid):
        """
        获取板块发帖所需要的标签
        返回两个数组 分别为tag1和tag2，每个数组内的元素为(tagid:int, name:str)
        例子：
        [(47, "内地"), (48, "国际")], []
        [(15, "问")], [(55, "实习")]
        """
        x = self.fetch("/board/{boardid}/tag".format(boardid=boardid))
        result = {1: [], 2: []}
        for layer in x:
            for tag in layer["tags"]:
                result[layer["layer"]].append((tag["id"], tag["name"]))
        return result[1], result[2]

    @auth
    def transfer_wealth(self, usernames, amount, reason):
        """
        对一些用户发起转账 向每个用户发送amount财富值
        但实际上对方只能收到min(amount*0.9, amount-10)财富值，例如想让对方收到1000则需要发送1111
        usernames: 用户名的数组
        wealth: int 每个用户发送多少
        reason: str 附言

        返回数组或错误字符串 如["username1", "username2"] 再如 "parameter_error"
        建议调用时将错误转为异常 assert isinstance(result, list), "transfer failed: "+result
        """
        x = self.s.put(self.ENDPOINT + "me/transfer-wealth",
                       data=json.dumps({"userNames": usernames, "wealth": amount, "reason": reason}),
                       headers={"content-type": "application/json"})
        try:
            return x.json()
        except:
            return x.text

    @auth
    def post_like(self, postid, action):
        """
        对帖子点赞action=="like"/点踩"dislike"
        返回{likeCount: 4, dislikeCount: 1, likeState: 2}
        """
        assert action in ["like", "dislike"]
        x = self.s.put(self.ENDPOINT + "post/" + str(postid) + "/like", data="1" if action == "like" else "2",
                       headers={"content-type": "application/json"})
        assert x.status_code == 200, "like PUT failed"
        x = self.s.get(self.ENDPOINT + "post/" + str(postid) + "/like")
        return x.json()

    @auth
    def get_followee_list(self, er="e"):
        """
        返回当前关注用户的用户id列表
        """
        from_ = 0
        result = []
        t = 0
        while len(result) == from_ and t < 50:
            x = self.fetch_real_real("me/followe{er}?from={from_}&size=20".format(**locals()))
            result.extend(x)
            from_ += 20
            t += 1  # 为了避免死循环，目前关注人数上限50，只需3次循环即可
        return result

    def get_follower_list(self):
        # 返回粉丝用户id列表, 最多返回1000条
        return self.get_followee_list(er="r")

    def set_headpic(self, url):
        # 设置当前用户头像url
        if url.startswith("//"):
            url = "https:" + url
        x = self.s.put(self.ENDPOINT + "me/portrait", '"' + url + '"', headers={"content-type": "application/json"})
        return x.status_code == 200

    def message_post(self, receiverId, content):
        # 向receiverId用户发送私信 内容content
        # 返回是否成功，错误信息
        id = int(receiverId)
        x = self.s.post(self.ENDPOINT + "message", json.dumps({"receiverId": id, "content": content}),
                        headers={"content-type": "application/json"})
        return x.status_code == 200, x.text


class CC98_API_V2_OAUTH(CC98_API_V2):
    """
    使用openid.cc98.org提供的OAuth进行登录
    """

    def __init__(self, client_id, client_secret, quoted_redirect_uri, code, proxy=None):
        """
        client_id client_secret可以在openid.cc98.org申请得到
        quoted_redirect_uri: 经过urllib.parse.quote后的redirect_uri
        code: 用户授权后得到的code
        proxy: 用于代理请求
        """
        self.s = requests.session()
        self.client_id = client_id
        self.client_secret = client_secret
        self.quoted_redirect_uri = quoted_redirect_uri
        if proxy:
            self.proxy = proxy
        else:
            self.proxy = []
        self.token, self.expiretime, self.refresh_token = self._login_oauth_code(client_id, client_secret,
                                                                                 quoted_redirect_uri, code)
        self.s.headers.update({"authorization": "Bearer " + self.token})
        self.username = self.fetch_real("me")["name"]

    def _login_oauth_code(self, client_id, client_secret, quoted_redirect_uri, code):
        """
        使用code得到access_token和refresh_token
        返回token,expiretime,refresh_token
        """
        x = self.s.post("https://openid.cc98.org/connect/token",
                        "grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&redirect_uri={quoted_redirect_uri}".format(
                            **locals()), headers={"content-type": "application/x-www-form-urlencoded"})
        data = x.json()
        refresh_token = data.get("refresh_token", None)
        return data["access_token"], int(time.time()) + data["expires_in"], refresh_token

    def login(self):
        """
        使用refresh_token 发起登录请求 以获取access_token 存入self.token
        并将过期时间写入self.expiretime
        """
        if self.refresh_token is None:
            raise LoginError("no refresh token")
        print("[Login using oauth] " + self.username)
        x = self.s.post("https://openid.cc98.org/connect/token",
                        "grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}".format(
                            client_id=self.client_id, client_secret=self.client_secret,
                            refresh_token=self.refresh_token),
                        headers={"content-type": "application/x-www-form-urlencoded"})
        data = x.json()
        token = data["access_token"]
        expirein = data["expires_in"]
        self.token = token
        self.expiretime = int(time.time()) + expirein
        self.refresh_token = data["refresh_token"]  # TODO: 并发问题
        self.s.headers.update({"authorization": "Bearer " + self.token})
