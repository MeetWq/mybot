import os
import re
import math
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from nonebot.log import logger

from .cc98api_base import CC98_API_V2, auth

dir_path = os.path.split(os.path.realpath(__file__))[0]

cache_path = os.path.join(dir_path, 'cache')
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

patterns = [(r'ac\d{2,4}', 'ac-mini'),
            (r'em\d{2}', 'em-mini'),
            (r'[acf]:?\d{3}', 'mahjong-mini'),
            (r'ms\d{2}', 'ms-mini'),
            (r'tb\d{2}', 'tb-mini')]


def get_emoji_path(name: str):
    name = name.strip().split('.')[0].replace(':', '')
    file_ext = ['.jpg', '.png', '.gif']
    for pattern, dir_name in patterns:
        if re.match(pattern, name):
            file_full_name = os.path.join(dir_path, 'images', dir_name, name)
            for ext in file_ext:
                file_path = file_full_name + ext
                if os.path.exists(file_path):
                    return file_path
    return None


class CC98Error(RuntimeError):
    def __init__(self):
        pass


class MyCC98Api(CC98_API_V2):
    def get_board_name(self, name):
        hot_topic_name = ['十大热门话题', '十大热门', '十大', '98十大', '热门']
        new_topic_name = ['新帖', '查看新帖', '查看最新', '最新帖子']
        score = process.extractOne(name, hot_topic_name)[1]
        if score > 80:
            board_name = '十大'
        else:
            score = process.extractOne(name, new_topic_name)[1]
            if score > 80:
                board_name = '新帖'
            else:
                board_all = self.board_all2()
                board_list = [board['name'] for board in board_all.values()]
                board_similar = process.extract(name, board_list)
                boards = []
                for board in board_similar:
                    boards.append([board[0], fuzz.ratio(board[0], name)])
                board_name, score = sorted(boards, key=lambda x: x[1], reverse=True)[0]
        return board_name, score

    def get_board_id(self, name):
        board_all = self.board_all2()
        for board in board_all.values():
            if board['name'] == name:
                return board['id']

    def get_topics(self, board_name):
        if board_name == '十大':
            return self.topic_hot()
        elif board_name == '新帖':
            return self.topic_new(size=10)
        else:
            board_id = self.get_board_id(board_name)
            return self.board_topic(board_id, size=10)

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

    def print_topics(self, topics):
        try:
            msg = ''
            count = 0
            for topic in topics:
                count += 1
                board_name = self.board(topic['boardId'])['name']
                title = topic['title']
                url = 'https://www.cc98.org/topic/' + str(topic['id'])
                msg += '[{}][{}]{}\n{}\n\n'.format(count, board_name, title, url)
            msg += '回复编号查看帖子内容'
            return msg
        except Exception as e:
            logger.exception(e)
            return None

    def replace_url(self, url):
        image_ext = ['.jpg', '.png', '.gif']
        if 'http://file.cc98.org/v2-upload/' not in url:
            return url
        if os.path.splitext(url)[-1] not in image_ext:
            return url
        file_name = os.path.basename(url)
        file_path = os.path.join(cache_path, file_name)
        if not os.path.exists(file_path):
            if not self.download(url, file_path):
                return url
        return "##file##{}##/file##".format(file_path)

    @staticmethod
    def replace_emoji(emoji):
        file_path = get_emoji_path(emoji)
        if file_path:
            return "##file##{}##/file##".format(file_path)
        else:
            return '[{}]'.format(emoji)

    def simplify_content(self, s):
        from_wechat = r'\[align=right\]\[size=3\]\[color=gray\]——来自微信小程序' \
                      r'「\[b\]\[color=black\]CC98\[/color\]\[/b\]」\[/color\]\[/size\]\[/align\]'
        s = re.sub(from_wechat, lambda x: '            ——来自微信小程序', s)

        quote_user = r'\[quote\]\[b\]以下是引用(\d*?)楼.*?\[/b\](.*)\[/quote\]'
        line = '\n- - - - - - - - - - - - - - -'
        while re.findall(quote_user, s, flags=re.S):
            # s = re.sub(quote_user, lambda x: ('# 以下是引用' + x.group(1) + '楼的发言：#' + x.group(2) + line), s, flags=re.S)
            s = re.sub(quote_user, lambda x: ('# 引用了' + x.group(1) + '楼的发言 #'), s, flags=re.S)
        quote_content = r'\[quote\](.*)\[/quote\]'
        while re.findall(quote_content, s, flags=re.S):
            s = re.sub(quote_content, lambda x: (' # 以下为引用内容：# ' + x.group(1) + line), s, flags=re.S)

        s = re.sub(r'\[b](.*?)\[/b]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[i](.*?)\[/i]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[u](.*?)\[/u]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[del](.*?)\[/del]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[align=.*?](.*?)\[/align]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[replyview](.*?)\[/replyview]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[size=\d*](.*?)\[/size]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[color=.*?](.*?)\[/color]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[url.*?](.*?)\[/url]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[img.*?](.*?)\[/img]', lambda x: self.replace_url(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[video](.*?)\[/video]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[bili](.*?)\[/bili]', lambda x: 'https://www.bilibili.com/video/av' + x.group(1), s, flags=re.S)
        s = re.sub(r'\[audio](.*?)\[/audio]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[upload.*?](.*?)\[/upload]', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'\[line]', line, s)
        s = re.sub(r'\[font=.*?](.*?)\[/font]', lambda x: x.group(1), s, flags=re.S)

        s = re.sub(r'!\[.*?]\((.*?)\)', lambda x: self.replace_url(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[source.*?]\((.*?)\)', lambda x: x.group(1), s, flags=re.S)

        s = re.sub(r'<div>(.*?)</div>', lambda x: x.group(1), s, flags=re.S)
        s = re.sub(r'<img src="(.*?)".*?>', lambda x: self.replace_url(x.group(1)), s, flags=re.S)

        s = re.sub(r'\[(ac\d{2,4})]', lambda x: self.replace_emoji(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[(em\d{2})]', lambda x: self.replace_emoji(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[([acf]:?\d{3})]', lambda x: self.replace_emoji(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[(ms\d{2})]', lambda x: self.replace_emoji(x.group(1)), s, flags=re.S)
        s = re.sub(r'\[(tb\d{2})]', lambda x: self.replace_emoji(x.group(1)), s, flags=re.S)

        return s

    def print_posts(self, topic, page):
        try:
            reply_num = topic["replyCount"] + 1
            page_num = math.ceil(reply_num / 10)
            start_num = (page - 1) * 10
            posts = self.topic_post(topic['id'], from_=start_num, size=10)
            board_name = self.board(topic['boardId'])['name']
            msg = '[{}]{}\n[page: {}/{}]\n\n'.format(board_name, topic['title'], page, page_num)

            count = start_num
            for post in posts:
                count += 1
                user_name = post['userName']
                content = self.simplify_content(post['content'])
                time = re.split('[T.+]', post['time'])
                post_time = time[0].replace('-', '/') + ' ' + time[1]
                msg += '[{}楼][{}]\n{}\n[{}]\n\n'.format(count, user_name, content, post_time)
            msg += '回复"+"、"-"翻页'
            return msg
        except Exception as e:
            logger.exception(e)
            return None
