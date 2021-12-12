import time
import httpx
import hashlib
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
trans_config = Config(**global_config.dict())


async def trans_baidu(text: str, lang_from: str, lang_to: str):
    salt = str(round(time.time() * 1000))
    app_id = trans_config.baidu_trans_app_id
    api_key = trans_config.baidu_trans_api_key
    sign_raw = app_id + text + salt + api_key
    sign = hashlib.md5(sign_raw.encode('utf8')).hexdigest()
    params = {
        'q': text,
        'from': lang_from,
        'to': lang_to,
        'appid': app_id,
        'salt': salt,
        'sign': sign
    }
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.json()
    return '\n'.join(res['dst'] for res in result['trans_result'])


async def trans_youdao(text: str, lang_from: str, lang_to: str):
    salt = str(round(time.time() * 1000))
    app_id = trans_config.youdao_trans_app_id
    api_key = trans_config.youdao_trans_api_key
    sign_raw = app_id + text + salt + api_key
    sign = hashlib.md5(sign_raw.encode('utf8')).hexdigest()
    params = {
        'q': text,
        'from': lang_from,
        'to': lang_to,
        'appKey': app_id,
        'salt': salt,
        'sign': sign
    }
    url = 'https://openapi.youdao.com/api'
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.json()
    return result['translation'][0]


async def trans_google(text: str, lang_from: str, lang_to: str):
    api_key = trans_config.google_trans_api_key

    async def detect_language(text: str):
        params = {
            'q': text,
            'key': api_key
        }
        url = 'https://translation.googleapis.com/language/translate/v2/detect'
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            result = resp.json()
        return result['data']['detections'][0][0]['language']

    if lang_from == 'auto':
        lang_from = await detect_language(text)
    params = {
        'q': text,
        'source': lang_from,
        'target': lang_to,
        'key': api_key
    }
    url = 'https://translation.googleapis.com/language/translate/v2'
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.json()
    return result['data']['translations'][0]['translatedText']


async def trans_bing(text: str, lang_from: str, lang_to: str):
    region = trans_config.bing_trans_region
    api_key = trans_config.bing_trans_api_key
    params = {
        'to': lang_to
    }
    if lang_from != 'auto':
        params['from'] = lang_from
    data = [{'Text': text}]
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Ocp-Apim-Subscription-Region': region
    }
    url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, params=params, json=data)
        result = resp.json()
    return '\n'.join(res['translations'][0]['text'] for res in result)


translator = {
    'baidu': trans_baidu,
    'youdao': trans_youdao,
    'google': trans_google,
    'bing': trans_bing
}


async def translate(text: str, engine: str, lang_from: str = 'auto', lang_to: str = 'zh'):
    text = text.replace('- ', '')
    try:
        trans = translator[engine]
        return await trans(text, lang_from, lang_to)
    except Exception as e:
        logger.warning(f'Error in {engine} translator: {e}')
        return ''
