import re
import requests
from config import *

login_url = 'http://www.nexushd.org/takelogin.php'
signin_url = 'http://www.nexushd.org/signin.php?'


class Users:
    def __init__(self, username, password, qq):
        self.username = username
        self.password = password
        self.qq = qq
        self.s = requests.Session()

    def login(self):
        login_params = {'username': self.username, 'password': self.password}
        x = self.s.post(login_url, data=login_params)
        return x.status_code == 200

    def signin(self):
        signin_params = {'action': 'post', 'content': '[em4]'}
        x = self.s.post(signin_url, data=signin_params)
        if x.status_code != 200:
            return None
        else:
            return re.findall(r'你已经连续签到 (\d*) 天，本次签到获得了 (\d*) 魔力值', x.text)[0]

    def signin_status(self):
        x = self.s.get(signin_url)
        return re.findall(r'你已经签到过了。请明天再来~', x.text)


users = [Users(nhd_username, nhd_password, my_qq)]
default_user = users[0]
