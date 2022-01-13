import httpx
import requests
from typing import Union
from http.cookies import SimpleCookie
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .qcloud_client import QCloudClient


async def search_qq(keyword, page=1, pagesize=1, number=1) -> Union[str, MessageSegment]:
    url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
    params = {
        'p': page,
        'n': pagesize,
        'w': keyword,
        'format': 'json'
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.json()
    if not result['data']['song']['list']:
        return 'QQ音乐中没有找到相关歌曲'
    songid = result['data']['song']['list'][number - 1]['songid']
    return MessageSegment.music('qq', songid)


async def search_netease(keyword, page=1, pagesize=1, number=1) -> Union[str, MessageSegment]:
    url = 'https://music.163.com/api/cloudsearch/pc'
    params = {
        's': keyword,
        'type': 1,
        'offset': page * pagesize - 1,
        'limit': pagesize
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, params=params)
        result = resp.json()
    if not result['result'].get('songs', []):
        return '网易云音乐中没有找到相关歌曲'
    songid = result['result']['songs'][number - 1]['id']
    return MessageSegment.music('163', songid)


async def search_kugou(keyword, page=1, pagesize=1, number=1) -> Union[str, MessageSegment]:
    search_url = 'http://mobilecdn.kugou.com/api/v3/search/song'
    params = {
        'format': 'json',
        'keyword': keyword,
        'showtype': 1,
        'page': page,
        'pagesize': pagesize
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(search_url, params=params)
        result = resp.json()
    if not result['data']['info']:
        return '酷狗音乐中没有找到相关歌曲'
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

    def parse_cookies(cookies_raw: str) -> dict:
        return {key: morsel.value for key, morsel in SimpleCookie(cookies_raw).items()}

    async with httpx.AsyncClient() as client:
        resp = await client.get(song_url, params=params, cookies=parse_cookies(cookies))
        result = resp.json()
    info = result['data']
    url = f'https://www.kugou.com/song/#hash={hash}&album_id={album_id}'
    audio = info['play_url']
    title = info['song_name']
    content = info['author_name']
    img_url = info['img']
    return MessageSegment.music_custom(url=url, audio=audio, title=title, content=content, img_url=img_url)


async def search_migu(keyword, page=1, pagesize=1, number=1) -> Union[str, MessageSegment]:
    url = 'https://m.music.migu.cn/migu/remoting/scr_search_tag'
    params = {
        'rows': pagesize,
        'type': 2,
        'keyword': keyword,
        'pgc': page
    }
    headers = {
        "Referer": "https://m.music.migu.cn"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers=headers)
        result = resp.json()
    if not result.get('musics', []):
        return '咪咕音乐中没有找到相关歌曲'
    info = result['musics'][number - 1]
    url = f"https://music.migu.cn/v3/music/song/{info['copyrightId']}"
    audio = info['mp3']
    title = info['title']
    content = info['singerName']
    img_url = info['cover']
    return MessageSegment.music_custom(url=url, audio=audio, title=title, content=content, img_url=img_url)


async def search_bilibili(keyword, page=1, pagesize=1, number=1) -> Union[str, MessageSegment]:
    search_url = 'https://api.bilibili.com/audio/music-service-c/s'
    params = {
        'page': page,
        'pagesize': pagesize,
        'search_type': 'music',
        'keyword': keyword
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(search_url, params=params)
        result = resp.json()
    if not result['data'].get('result', []):
        return 'B站音频区中没有找到相关歌曲'
    info = result['data']['result'][number - 1]
    url = f"https://www.bilibili.com/audio/au{info['id']}"
    audio = info['play_url_list'][0]['url']
    title = info['title']
    content = info['author']
    img_url = info['cover']

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'referer': 'https://www.bilibili.com/'
    }
    stream = requests.get(audio, headers=headers)
    qcloud_client = QCloudClient()
    audio = qcloud_client.put_object(
        stream, f"bilibili_music/{info['id']}.m4a")

    return MessageSegment.music_custom(url=url, audio=audio, title=title, content=content, img_url=img_url)


sources = {
    'qq': {
        'aliases': {'点歌', 'qq点歌', 'QQ点歌'},
        'func': search_qq
    },
    'netease': {
        'aliases': {'网易点歌', '网易云点歌'},
        'func': search_netease
    },
    'kugou': {
        'aliases': {'酷狗点歌'},
        'func': search_kugou
    },
    'migu': {
        'aliases': {'咪咕点歌'},
        'func': search_migu
    },
    'bilibili': {
        'aliases': {'b站点歌', 'B站点歌', 'bilibili点歌'},
        'func': search_bilibili
    },
}


async def search_song(source: str, keyword: str) -> Union[str, MessageSegment]:
    try:
        func = sources[source]['func']
        return await func(keyword)
    except Exception as e:
        logger.warning(
            f"Error in search_song({keyword}, {source}): {e}")
        return None
