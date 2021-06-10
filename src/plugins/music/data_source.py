import json
import aiohttp
import traceback
from http.cookies import SimpleCookie
from nonebot.log import logger
from nonebot.adapters.cqhttp import MessageSegment


async def search_song(keyword, source='qq'):
    try:
        msg = None
        if source == 'qq':
            msg = await search_qq(keyword)
        elif source == 'netease':
            msg = await search_netease(keyword)
        elif source == 'kugou':
            msg = await search_kugou(keyword)
        elif source == 'migu':
            msg = await search_migu(keyword)
        elif source == 'bilibili':
            msg = await search_bilibili(keyword)
        return msg
    except (TypeError, KeyError, IndexError):
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
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.read()
    result = json.loads(data)
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
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            data = await resp.read()
    result = json.loads(data)
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
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, params=params) as resp:
            data = await resp.read()
    result = json.loads(data)
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

    async with aiohttp.ClientSession() as session:
        async with session.get(song_url, params=params, cookies=parse_cookies(cookies)) as resp:
            data = await resp.read()
    result = json.loads(data)
    info = result['data']
    url = 'https://www.kugou.com/song/#hash={}&album_id={}'.format(hash, album_id)
    audio = info['play_url']
    title = info['song_name']
    content = info['author_name']
    img_url = info['img']
    return MessageSegment.music_custom(url=url, audio=audio, title=title, content=content, img_url=img_url)


async def search_migu(keyword, page=1, pagesize=1, number=1):
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
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            result = await resp.json()
    info = result['musics'][number - 1]
    url = f"https://music.migu.cn/v3/music/song/{info['copyrightId']}"
    audio = info['mp3']
    title = info['title']
    content = info['singerName']
    img_url = info['cover']
    return MessageSegment.music_custom(url=url, audio=audio, title=title, content=content, img_url=img_url)


async def search_bilibili(keyword, page=1, pagesize=1, number=1):
    search_url = 'https://api.bilibili.com/audio/music-service-c/s'
    params = {
        'page': page,
        'pagesize': pagesize,
        'search_type': 'music',
        'keyword': keyword
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url, params=params) as resp:
            data = await resp.read()
    result = json.loads(data)
    info = result['data']['result'][number - 1]
    url = 'https://www.bilibili.com/audio/au{}'.format(info['id'])
    audio = info['play_url_list'][0]['url']
    title = info['title']
    content = info['author']
    img_url = info['cover']
    return MessageSegment.music_custom(url=url, audio=audio, title=title, content=content, img_url=img_url)


def parse_cookies(cookies_raw: str) -> dict:
    return {key: morsel.value for key, morsel in SimpleCookie(cookies_raw).items()}
