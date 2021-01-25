import json
import aiohttp
import traceback
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
tuling_config = Config(**global_config.dict())


async def call_tuling_api(text, user_id):
    if not text:
        return None

    url = 'http://openapi.tuling123.com/openapi/api/v2'

    payload = {
        'reqType': 0,
        'perception': {
            'inputText': {
                'text': text
            }
        },
        'userInfo': {
            'apiKey': tuling_config.tuling_apikey,
            'userId': user_id
        }
    }

    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload) as response:
                if response.status != 200:
                    return None

                resp_payload = json.loads(await response.text())
                if resp_payload['results']:
                    for result in resp_payload['results']:
                        if result['resultType'] == 'text':
                            return result['values']['text']
    except (aiohttp.ClientError, json.JSONDecodeError, KeyError):
        logger.warning('Error in calling tuling API: {}'.format(traceback.format_exc()))
        return None
