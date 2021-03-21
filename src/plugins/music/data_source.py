import requests
import traceback
from http.cookies import SimpleCookie
from nonebot.log import logger
from nonebot.adapters.cqhttp import escape, MessageSegment


xml_card = '''<?xml version="1.0" encoding="utf-8"?>
<msg serviceID="2" templateID="1" action="web" brief="[音乐] {title}" sourceMsgId="0" url="{jump_url}" flag="0" adverSign="0" multiMsgFlag="0">
    <item layout="2">
        <audio cover="{cover_url}" src="{music_url}"/>
        <title>{title}</title>
        <summary>{author}</summary>
    </item>
    <source name="{source}" icon="{icon}"/>
</msg>
'''


async def search_song(keyword, source='qq'):
    try:
        msg = None
        if source == 'qq':
            msg = await search_qq(keyword)
        elif source == 'netease':
            msg = await search_netease(keyword)
        elif source == 'kugou':
            msg = await search_kugou(keyword)
        return msg
    except (TypeError, KeyError, IndexError, requests.exceptions.RequestException):
        logger.debug(traceback.format_exc())
        return None


async def search_qq(keyword, page=1, pagesize=1, number=1):
    url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
    params = {
        'p': page,
        'n': pagesize,
        'w': keyword,
        'format': 'json'
    }
    result = requests.get(url, params=params).json()
    songid = result['data']['song']['list'][number - 1]['songid']
    return MessageSegment.music('qq', songid)


async def search_netease(keyword, page=1, pagesize=1, number=1):
    url = 'https://music.163.com/api/cloudsearch/pc'
    params = {
        's': keyword,
        'type': 1,
        'offset': page * pagesize - 1,
        'limit': pagesize
    }
    result = requests.post(url, params=params).json()
    songid = result['result']['songs'][number - 1]['id']
    return MessageSegment.music('163', songid)


async def search_kugou(keyword, page=1, pagesize=1, number=1):
    search_url = 'http://mobilecdn.kugou.com/api/v3/search/song'
    params = {
        'format': 'json',
        'keyword': keyword,
        'showtype': 1,
        'page': page,
        'pagesize': pagesize
    }
    result = requests.get(search_url, params=params).json()
    hash = result['data']['info'][number - 1]['hash']
    album_id = result['data']['info'][number - 1]['album_id']
    song_url = 'https://wwwapi.kugou.com/yy/index.php'
    params = {
        'r': 'play/getdata',
        'hash': hash,
        'album_id': album_id
    }
    cookies = 'kg_mid=30f1713c23ab7bb496ab035b07dae834; ' \
        'ACK_SERVER_10015=%7B%22list%22%3A%5B%5B%22bjlogin-user.kugou.com%22%5D%5D%7D; '\
        'ACK_SERVER_10016=%7B%22list%22%3A%5B%5B%22bjreg-user.kugou.com%22%5D%5D%7D; ' \
        'ACK_SERVER_10017=%7B%22list%22%3A%5B%5B%22bjverifycode.service.kugou.com%22%5D%5D%7D; ' \
        'Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1598198881; kg_dfid=1HZmYL0ngIYp0uu93N2m4s5P; ' \
        'kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e; ' \
        'Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1598199021'
    result = requests.get(song_url, params=params,
                          cookies=parse_cookies(cookies)).json()
    info = result['data']
    title = info['song_name']
    author = info['author_name']
    cover_url = info['img']
    music_url = info['play_url']
    jump_url = 'https://www.kugou.com/song/#hash={}&album_id={}'.format(
        hash, album_id)
    source = '酷狗音乐'
    icon = 'https://img.imgdb.cn/item/605614e1524f85ce29fa0c11.png'
    xml_str = xml_card.format(title=title, author=author,
                              cover_url=cover_url, music_url=music_url, jump_url=jump_url,
                              source=source, icon=icon)
    return MessageSegment.xml(escape(xml_str))


def parse_cookies(cookies_raw: str) -> dict:
    return {key: morsel.value for key, morsel in SimpleCookie(cookies_raw).items()}
