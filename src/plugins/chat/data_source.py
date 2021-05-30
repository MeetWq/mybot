import json
import uuid
import random
import aiohttp
import requests
from pathlib import Path
from cachetools import TTLCache
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

global_config = get_driver().config
chat_config = Config(**global_config.dict())


class ChatBot:
    def __init__(self):
        self.api_key = chat_config.baidu_unit_api_key
        self.secret_key = chat_config.baidu_unit_secret_key
        self.bot_id = chat_config.baidu_unit_bot_id
        self.base_url = 'https://aip.baidubce.com'
        self.token = self.get_token()
        self.sessions = TTLCache(maxsize=128, ttl=60 * 60 * 1)

    def get_token(self):
        url = f'{self.base_url}/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}'
        response = requests.post(url).json()
        return response['access_token']

    async def get_reply(self, text: str, user_id: str) -> str:
        url = f'{self.base_url}/rpc/2.0/unit/service/chat?access_token={self.token}'
        session_id = self.sessions.get(user_id)
        if not session_id:
            session_id = ''
        params = {
            'log_id': str(uuid.uuid4()),
            'version': '2.0',
            'service_id': self.bot_id,
            'session_id': session_id,
            'request': {
                'query': text,
                'user_id': user_id
            },
            'dialog_state': {
                'contexts': {
                    'SYS_REMEMBERED_SKILLS': ['1098087', '1098084', '1098089']
                }
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(params, ensure_ascii=False)) as resp:
                response = await resp.json()
        if response and response['error_code'] == 0:
            session_id = response['result']['session_id']
            self.sessions[user_id] = session_id
            return response['result']['response_list'][0]['action_list'][0]['say']
        else:
            logger.debug(response)
            return ''


async def get_anime_thesaurus(text):
    thesaurus_path = Path('src/libs/AnimeThesaurus/data.json')
    thesaurus_data = json.load(thesaurus_path.open('r', encoding='utf-8'))
    if text in thesaurus_data:
        return random.choice(thesaurus_data[text])
    return ''


chat_bot = ChatBot()
