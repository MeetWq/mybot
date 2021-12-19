import os
import re
import math
from thefuzz import process
from typing import List, Tuple, Union
from nonebot import get_driver
from nonebot.adapters.cqhttp.message import MessageSegment

from .cc98api_base import CC98_API_V2
from .emoji import get_emoji, emoji_list
from .config import Config

global_config = get_driver().config
cc98_config = Config(**global_config.dict())


class MyCC98Api(CC98_API_V2):
    async def topic(self, id: int):
        return super().topic(id)

    async def get_board_name(self, name: str) -> Tuple[str, float]:
        hot_topic_name = ['十大热门话题', '十大热门', '十大', '98十大', '热门']
        new_topic_name = ['新帖', '查看新帖', '查看最新', '最新帖子']

        score = process.extractOne(name, hot_topic_name)[1]
        if score > 80:
            return '十大', score

        score = process.extractOne(name, new_topic_name)[1]
        if score > 80:
            return '新帖', score

        board_all = self.board_all2()
        board_list = [board['name'] for board in board_all.values()]
        return process.extractOne(name, board_list)

    async def get_board_id(self, name: str) -> int:
        board_all = self.board_all2()
        for board in board_all.values():
            if board['name'] == name:
                return board['id']
        return 0

    async def get_topics(self, board_name: str):
        if board_name == '十大':
            return self.topic_hot()
        elif board_name == '新帖':
            return self.topic_new(size=10)
        else:
            board_id = await self.get_board_id(board_name)
            return self.board_topic(board_id, size=10)

    async def download(self, url: str) -> bytes:
        x = self.s.get(url)
        if x.status_code == 200:
            return x.content
        return None

    async def print_topics(self, topics: List[dict]) -> List[str]:
        msgs = []
        for topic in topics:
            board_name = self.board(topic['boardId'])['name']
            msgs.append(f"[{topic['id']}][{board_name}]{topic['title']}")
        return msgs

    async def print_posts(self, topic: dict, page: int) -> List[str]:
        msgs = []
        board_name = self.board(topic['boardId'])['name']
        reply_num = topic["replyCount"] + 1
        page_num = math.ceil(reply_num / 10)
        msgs.append(
            f"[{board_name}]{topic['title']}\n[page: {page}/{page_num}]")

        start_num = (page - 1) * 10
        posts = self.topic_post(topic['id'], from_=start_num, size=10)

        for i, post in enumerate(posts, start=start_num+1):
            user_name = post['userName']
            content = await self.simplify_content(post['content'])
            time = re.split('[T.+]', post['time'])
            post_time = time[0].replace('-', '/') + ' ' + time[1]
            msgs.append(f'[{i}楼][{user_name}]\n{content}\n[{post_time}]')
        msgs.append('回复"+"、"-"翻页')
        return msgs

    async def replace_url(self, url: str) -> Union[str, MessageSegment]:
        image_ext = ['.jpg', '.png', '.gif']
        if 'http://file.cc98.org/v2-upload/' not in url:
            return url
        if os.path.splitext(url)[-1] not in image_ext:
            return url
        data = await self.download(url)
        if data:
            return MessageSegment.image(data)
        else:
            return url

    async def replace_emoji(self, emoji: str) -> Union[str, MessageSegment]:
        emoji = emoji.lower()
        dir_name = ''
        for _, params in emoji_list.items():
            if re.fullmatch(params['pattern'], emoji):
                dir_name = params['dir_name']
        if dir_name:
            data = await get_emoji(dir_name, emoji)
            return MessageSegment.image(data)
        else:
            return f'[{emoji}]'

    async def simplify_content(self, s: str):
        s = s.replace(
            '[align=right][size=3][color=gray]——来自微信小程序'
            '「[b][color=black]CC98[/color][/b]」[/color][/size][/align]',
            '            ——来自微信小程序')

        quote_user = r'\[quote\]\[b\]以下是引用(\d*?)楼.*?\[/b\](.*)\[/quote\]'
        line = '\n- - - - - - - - - - - - - - -'
        while re.findall(quote_user, s, flags=re.S):
            s = re.sub(quote_user, lambda x: (
                '# 引用了' + x.group(1) + '楼的发言 #' + x.group(2) + line), s, flags=re.S)
        quote_content = r'\[quote\](.*)\[/quote\]'
        while re.findall(quote_content, s, flags=re.S):
            s = re.sub(quote_content, lambda x: (
                ' # 以下为引用内容：# ' + x.group(1) + line), s, flags=re.S)

        ignore_patterns = [
            r'\[b](.*?)\[/b]',
            r'\[i](.*?)\[/i]',
            r'\[u](.*?)\[/u]',
            r'\[del](.*?)\[/del]',
            r'\[align=.*?](.*?)\[/align]',
            r'\[replyview](.*?)\[/replyview]',
            r'\[size=\d*](.*?)\[/size]',
            r'\[color=.*?](.*?)\[/color]',
            r'\[url.*?](.*?)\[/url]',
            r'\[video](.*?)\[/video]',
            r'\[audio](.*?)\[/audio]',
            r'\[upload.*?](.*?)\[/upload]',
            r'\[font=.*?](.*?)\[/font]',
            r'\[source.*?]\((.*?)\)',
            r'<div>(.*?)</div>'
        ]
        for p in ignore_patterns:
            s = re.sub(p, lambda x: x.group(1), s, flags=re.S)

        s = re.sub(r'\[bili](.*?)\[/bili]',
                   lambda x: 'https://www.bilibili.com/video/av' + x.group(1), s, flags=re.S)
        s = re.sub(r'\[line]', line, s)

        img_patterns = [
            r'\[img.*?](.*?)\[/img]',
            r'!\[.*?]\((.*?)\)',
            r'<img src="(.*?)".*?>'
        ]
        for p in img_patterns:
            s = re.sub(
                p, lambda x: f"##img##{x.group(1)}##/img##", s, flags=re.S)

        emoji_patterns = [
            r'\[(ac\d{2,4})]',
            r'\[(em\d{2})]',
            r'\[([acf]:?\d{3})]',
            r'\[(ms\d{2})]',
            r'\[(tb\d{2})]',
            r'\[([Cc][Cc]98\d{2})]'
        ]
        for p in emoji_patterns:
            s = re.sub(
                p, lambda x: f"##emoji##{x.group(1)}##/emoji##", s, flags=re.S)

        return s


cc98_api = MyCC98Api(cc98_config.cc98_user_name,
                     cc98_config.cc98_user_password)
