import os
import json
import math
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from nonebot.log import logger

from my.plugins.cc98.cc98api.cc98api_base import CC98_API_V2, auth
from .qcloud_client import *
from .xiaomark import get_short_url


class CC98Error(RuntimeError):
    def __init__(self):
        pass


class MyCC98Api(CC98_API_V2):
    # 下载一张图片
    @auth
    def download(self, url, path):
        x = self.s.get(url)
        status = x.status_code == 200
        if status:
            try:
                with open(path, 'wb') as f:
                    f.write(x.content)
            except Exception as e:
                logger.warning('file write failed', str(e))
                status = False
        else:
            logger.warning('download failed')
        return status

    def get_signin_data(self):
        topic_id = 4766164
        topic = self.topic(topic_id)
        posts = self.topic_post(topic_id, from_=topic["replyCount"] - 9, size=10)
        # 用yield来遍历整个帖子，逆序 也就是说最新的回复会优先返回
        for post in posts[::-1]:
            if post['userName'] == self.username:
                return re.findall(r'\[b\](.*?)\[/b\]', post['content'])
        return None

    def search_board(self, name):
        board_all = self.board_all2()
        board_list = [board['name'] for board in board_all.values()]
        board_similar = process.extract(name, board_list)
        boards = []
        for board in board_similar:
            boards.append([board[0], fuzz.ratio(board[0], name)])
        return sorted(boards, key=lambda x: x[1], reverse=True)[0]

    def get_board_id(self, name):
        board_all = self.board_all2()
        for board in board_all.values():
            if board['name'] == name:
                return board['id']

    def print_topics(self, topics):
        try:
            msgs = []
            msg = ''
            max_length = 950  # 992
            count = 0
            for topic in topics:
                count += 1
                msg_new = '[' + str(count) + ']'
                board_name = self.board(topic['boardId'])['name']
                msg_new += '[' + board_name + ']'
                msg_new += topic['title'] + '\n'
                msg_new += 'https://www.cc98.org/topic/' + str(topic['id']) + '\n\n'
                if len(msg + msg_new) > max_length:
                    msgs.append(msg)
                    msg = msg_new
                else:
                    msg += msg_new
            msg += '输入编号查看帖子内容'
            msgs.append(msg)
            return msgs
        except Exception as e:
            logger.exception(e)
            raise CC98Error

    def replace_url(self, url):
        if 'http://file.cc98.org/v2-upload/' not in url:
            return url

        filename = os.path.basename(url)
        key = filename.split('.')[0]
        json_path = os.path.join('my', 'data', 'data_list.json')
        with open(json_path, "r") as f:
            data_list = json.load(f)
        if key not in data_list.keys():
            path = os.path.join('my', 'data', 'cc98', filename)
            if not os.path.exists(path):
                if not self.download(url, path):
                    return url
            qcloud_url = qcloud_client.upload_file(path, filename)
            if not qcloud_url:
                return url
            short_url = get_short_url(qcloud_url)
            if not short_url:
                return qcloud_url
            data_list[key] = short_url
            with open(json_path, "w") as f:
                json.dump(data_list, f, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            short_url = data_list[key]
        return short_url

    def simplify_content(self, s):
        from_wechat = r'\[align=right\]\[size=3\]\[color=gray\]——来自微信小程序' \
                      r'「\[b\]\[color=black\]CC98\[/color\]\[/b\]」\[/color\]\[/size\]\[/align\]'
        s = re.sub(from_wechat, lambda x: '            ——来自微信小程序', s)

        quote_user = r'\[quote\]\[b\]以下是引用(\d*?)楼.*?\[/b\](.*)\[/quote\]'
        line = '\n- - - - - - - - - - - - - - - -'
        while re.findall(quote_user, s, flags=re.S):
            s = re.sub(quote_user, lambda x: ('# 以下是引用' + x.group(1) + '楼的发言：#' + x.group(2) + line),
                       s, flags=re.S)
        quote_content = r'\[quote\](.*)\[/quote\]'
        while re.findall(quote_content, s, flags=re.S):
            s = re.sub(quote_content, lambda x: (' # 以下为引用内容：# ' + x.group(1) + line), s, flags=re.S)

        s = re.sub(r'\[b\](.*?)\[/b\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[i\](.*?)\[/i\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[u\](.*?)\[/u\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[del\](.*?)\[/del\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[align=.*?\](.*?)\[/align\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[replyview\](.*?)\[/replyview\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[size=\d*\](.*?)\[/size\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[color=.*?\](.*?)\[/color\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[url.*?\](.*?)\[/url\]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[img.*?\](.*?)\[/img\]', lambda x: self.replace_url(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[video\](.*?)\[/video\]', lambda x: self.replace_url(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[bili\](.*?)\[/bili\]', lambda x: 'https://www.bilibili.com/video/av' + x.group(1), s, flags=re.S)
        s = re.sub(r'\[audio\](.*?)\[/audio\]', lambda x: self.replace_url(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[upload.*?\](.*?)\[/upload\]', lambda x: self.replace_url(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[line\]', line, s)
        s = re.sub(r'\[font=.*?\](.*?)\[/font\]', lambda x: x.group(1), s, flags=re.S)

        s = re.sub(r'!\[.*?\]\((.*?)\)', lambda x: self.replace_url(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[source.*?\]\((.*?)\)', lambda x: x.group(1), s, flags=re.S)

        s = re.sub(r'<div>(.*?)</div>', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'<img src="(.*?)".*?>', lambda x: self.replace_url(x.group(1)), s, flags=re.S)

        return s

    def print_posts(self, topic, page):
        try:
            reply_num = topic["replyCount"] + 1
            page_num = math.ceil(reply_num / 10)
            start_num = (page - 1) * 10
            posts = self.topic_post(topic['id'], from_=start_num, size=10)
            board_name = self.board(topic['boardId'])['name']
            page_count = '[page: ' + str(page) + '/' + str(page_num) + ']'
            title = '[' + board_name + ']' + topic['title'] + '\n' + page_count + '\n\n'

            msgs = []
            msg = title
            max_length = 500  # 992
            count = start_num
            for post in posts:
                count += 1
                post_title = '[' + str(count) + '楼]' + '[' + post['userName'] + ']\n'
                post_content = self.simplify_content(post['content']) + '\n'
                post_time = re.split('[T.+]', post['time'])
                post_time = '[' + post_time[0].replace('-', '/') + ' ' + post_time[1] + ']\n\n'
                if len(msg + post_content) > max_length:
                    if len(msg) > max_length * 2 / 3:
                        msgs.append(msg)
                        msg = ''
                    msg += post_title
                    while len(msg + post_content) > max_length:
                        length = max_length - len(msg)
                        while re.match(r'[a-zA-Z0-9:.\\/_\-\[\]]', post_content[length]):
                            length += 1
                        msg += post_content[0:length]
                        msgs.append(msg)
                        msg = ''
                        post_content = post_content[length:]
                    msg += post_content
                    msg += post_time
                else:
                    msg_new = post_title + post_content + post_time
                    msg += msg_new
            msg += '输入"+"、"-"翻页'
            msgs.append(msg)
            return msgs
        except Exception as e:
            logger.exception(e)
            raise CC98Error

    def get_topics(self, name):
        hot_topic_name = ['十大热门话题', '十大热门', '十大', '98十大', '热门']
        new_topic_name = ['新帖', '查看新帖', '查看最新', '最新帖子']
        score = process.extractOne(name, hot_topic_name)[1]
        if score > 80:
            topics = self.topic_hot()
            board_name = '十大'
        else:
            score = process.extractOne(name, new_topic_name)[1]
            if score > 80:
                topics = self.topic_new(from_=0, size=20)
                board_name = '新帖'
            else:
                board_name, score = self.search_board(name)
                board_id = self.get_board_id(board_name)
                topics = self.board_topic(board_id, from_=0, size=10)
        return board_name, topics, score
