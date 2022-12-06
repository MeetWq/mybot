import json
import uuid
import httpx
import random
from pathlib import Path
from cachetools import TTLCache
from typing import Optional, Dict

from nonebot import get_driver
from nonebot.log import logger

from .config import Config

chat_config = Config.parse_obj(get_driver().config.dict())

dir_path = Path(__file__).parent
data_path = dir_path / "resources"


class BaiduUnit:
    def __init__(self):
        self.api_key = chat_config.baidu_unit_api_key
        self.secret_key = chat_config.baidu_unit_secret_key
        self.bot_id = chat_config.baidu_unit_bot_id
        self.base_url = "https://aip.baidubce.com"
        self.token = ""
        self.sessions = TTLCache(maxsize=128, ttl=60 * 60 * 1)

    async def refresh_token(self):
        try:
            url = f"{self.base_url}/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
            async with httpx.AsyncClient() as client:
                resp = await client.post(url)
                result = resp.json()
            self.token = result.get("access_token", "")
        except Exception as e:
            logger.warning(f"Error in refresh_token: {e}")

    async def get_reply(self, text: str, event_id: str, user_id: str) -> str:
        if not self.token:
            await self.refresh_token()
            if not self.token:
                return ""

        url = f"{self.base_url}/rpc/2.0/unit/service/chat?access_token={self.token}"
        session_id = self.sessions.get(event_id)
        if not session_id:
            session_id = ""
        params = {
            "log_id": str(uuid.uuid4()),
            "version": "2.0",
            "service_id": self.bot_id,
            "session_id": session_id,
            "request": {"query": text, "user_id": user_id},
            "dialog_state": {
                "contexts": {"SYS_REMEMBERED_SKILLS": ["1098087", "1098084", "1098089"]}
            },
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=params)
                result = resp.json()

            session_id = result["result"]["session_id"]
            self.sessions[event_id] = session_id
            return result["result"]["response_list"][0]["action_list"][0]["say"]
        except Exception as e:
            logger.warning(f"Error in get_reply({text}, {event_id}, {user_id}): {e}")
            return ""


proxies = chat_config.http_proxy


class ChatGPT:
    def __init__(self):
        self.session_token: str = chat_config.chatgpt_session_token
        self.authorization: Optional[str] = None
        self.sessions = TTLCache(maxsize=128, ttl=60 * 60 * 1)

    def get_id(self) -> str:
        return str(uuid.uuid4())

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.authorization}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        }

    async def refresh_token(self):
        SESSION_TOKEN = "__Secure-next-auth.session-token"
        cookies = {SESSION_TOKEN: self.session_token}
        async with httpx.AsyncClient(proxies=proxies) as client:
            resp = await client.get(
                "https://chat.openai.com/api/auth/session",
                headers=self.headers,
                cookies=cookies,
                timeout=60 * 3,
            )
        try:
            self.session_token = resp.cookies.get(SESSION_TOKEN) or ""
            self.authorization = resp.json()["accessToken"]
            logger.info(f"session_token: {self.session_token}")
            logger.info(f"authorization: {self.authorization}")
        except Exception as e:
            logger.warning(f"Error in refresh_token: {e}\nresp: {resp.text}")

    async def get_reply(self, text: str, event_id: str, user_id: str) -> str:
        if not self.authorization:
            await self.refresh_token()

        if session := self.sessions.get(event_id, {}):
            conversation_id = session.get("conversation_id")
            parent_id = session.get("parent_id")
        else:
            conversation_id = None
            parent_id = self.get_id()

        data = {
            "action": "next",
            "messages": [
                {
                    "id": self.get_id(),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [text]},
                }
            ],
            "conversation_id": conversation_id,
            "parent_message_id": parent_id,
            "model": "text-davinci-002-render",
        }

        async with httpx.AsyncClient(proxies=proxies) as client:
            resp = await client.post(
                "https://chat.openai.com/backend-api/conversation",
                json=data,
                headers=self.headers,
                timeout=60 * 3,
            )

        try:
            result = resp.text.splitlines()[-4]
            result = result[6:]
        except:
            logger.warning(f"Abnormal response content: {resp.text}")
            return ""
        result = json.loads(result)
        session = {
            "conversation_id": result["conversation_id"],
            "parent_id": result["message"]["id"],
        }
        self.sessions[event_id] = session
        return result["message"]["content"]["parts"][0]


thesaurus_path = data_path / "anime_thesaurus.json"
thesaurus_data = json.load(thesaurus_path.open("r", encoding="utf-8"))


async def get_anime_thesaurus(text):
    if text in thesaurus_data:
        return random.choice(thesaurus_data[text])
    return ""


chat_bot = ChatGPT()
