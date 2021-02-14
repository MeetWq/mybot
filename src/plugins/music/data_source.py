import requests
from urllib.parse import quote

QQ_MUSIC_SEARCH_URL_FORMAT = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?' \
                             'g_tk=5381&p=1&n=20&w={}&format=json&loginUin=0&' \
                             'hostUin=0&inCharset=utf8&outCharset=utf-8&notice=0&' \
                             'platform=yqq&needNewCode=0&remoteplace=txt.yqq.song&' \
                             't=0&aggr=1&cr=1&catZhida=1&flag_qc=0'


async def search_song_id(keyword):
    try:
        keyword = quote(keyword)
        resp = requests.get(QQ_MUSIC_SEARCH_URL_FORMAT.format(keyword))
        payload = resp.json()
        if not isinstance(payload, dict) or payload.get('code') != 0 or not payload.get('data'):
            return None
        return payload['data']['song']['list'][0]['songid']
    except (TypeError, KeyError, IndexError, requests.exceptions.RequestException):
        return None
