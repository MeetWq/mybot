from .my_cc98api import MyCC98Api
from config import *


class Users:
    def __init__(self, username, password, qq):
        self.username = username
        self.password = password
        self.qq = qq
        self.api = MyCC98Api(username, password)


users = [Users(cc98_username1, cc98_password1, my_qq),
         Users(cc98_username2, cc98_password2, my_qq),
         Users(cc98_username3, cc98_password3, my_qq),
         Users(cc98_username4, cc98_password4, my_qq)]
default_user = users[1]
