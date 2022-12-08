import json
import uuid
import httpx
from cachetools import TTLCache
from typing import Optional, Dict

from nonebot import get_driver
from nonebot.log import logger

from .config import Config

chatgpt_config = Config.parse_obj(get_driver().config.dict())


class ChatGPT:
    def __init__(self):
        self.session_token: str = chatgpt_config.chatgpt_session_token
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
        async with httpx.AsyncClient() as client:
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

    async def get_reply(self, text: str, session_id: str) -> str:
        if not self.authorization:
            await self.refresh_token()

        if session := self.sessions.get(session_id, {}):
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

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://chat.openai.com/backend-api/conversation",
                json=data,
                headers=self.headers,
                timeout=60 * 3,
            )

        try:
            result = resp.text.splitlines()[-4]
            result = result[6:]
        except Exception as e:
            logger.warning(f"Abnormal response content: {resp.text}")
            raise e
        result = json.loads(result)
        session = {
            "conversation_id": result["conversation_id"],
            "parent_id": result["message"]["id"],
        }
        self.sessions[session_id] = session
        return result["message"]["content"]["parts"][0]

    def refresh_session(self, session_id: str):
        self.sessions[session_id] = {}


chat_bot = ChatGPT()
