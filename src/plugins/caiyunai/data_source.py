import httpx
import traceback
from typing import List
from nonebot import get_driver
from nonebot.log import logger

from .config import Config

caiyun_config = Config.parse_obj(get_driver().config.dict())

model_list = {
    '小梦0号': {
        'name': '小梦0号',
        'id': '60094a2a9661080dc490f75a'
    },
    '小梦1号': {
        'name': '小梦1号',
        'id': '601ac4c9bd931db756e22da6'
    },
    '纯爱': {
        'name': '纯爱小梦',
        'id': '601f92f60c9aaf5f28a6f908'
    },
    '言情': {
        'name': '言情小梦',
        'id': '601f936f0c9aaf5f28a6f90a'
    },
    '玄幻': {
        'name': '玄幻小梦',
        'id': '60211134902769d45689bf75'
    }
}


class CaiyunError(Exception):
    pass


class NetworkError(CaiyunError):
    pass


class AccountError(CaiyunError):
    pass


class ContentError(CaiyunError):
    pass


class CaiyunAi:
    def __init__(self):
        self.model: str = '小梦0号'
        self.token: str = caiyun_config.caiyunai_apikey
        self.nid: str = ''
        self.branchid: str = ''
        self.nodeid: str = ''
        self.nodeids: List[str] = []
        self.result: str = ''
        self.content: str = ''
        self.contents: List[str] = []
        self.err_msg: str = ''

    async def get_contents(self):
        self.err_msg = ''
        try:
            if not self.nid:
                await self.novel_save()
            await self.add_node()
            self.result += self.content
            await self.novel_ai()
        except CaiyunError as e:
            self.err_msg = str(e)
            logger.warning(traceback.format_exc())
        except:
            self.err_msg = '未知错误'
            logger.warning(traceback.format_exc())

    async def novel_save(self):
        url = f'http://if.caiyunai.com/v2/novel/{self.token}/novel_save'
        params = {
            'content': self.content,
            'title': '',
            'ostype': ''
        }
        result = await self.post(url, json=params)
        data = result['data']
        self.nid = data['nid']
        self.branchid = data['novel']['branchid']
        self.nodeid = data['novel']['firstnode']
        self.nodeids = [self.nodeid]

    async def add_node(self):
        url = f'http://if.caiyunai.com/v2/novel/{self.token}/add_node'
        params = {
            'nodeids': self.nodeids,
            'choose': self.nodeid,
            'nid': self.nid,
            'value': self.content,
            'ostype': '',
            'lang': 'zh'
        }
        await self.post(url, json=params)

    async def novel_ai(self) -> List[dict]:
        url = f'http://if.caiyunai.com/v2/novel/{self.token}/novel_ai'
        params = {
            'nid': self.nid,
            'content': self.content,
            'uid': self.token,
            'mid': model_list[self.model]['id'],
            'title': '',
            'ostype': '',
            'status': 'http',
            'lang': 'zh',
            'branchid': self.branchid,
            'lastnode': self.nodeid
        }
        result = await self.post(url, json=params)
        nodes = result['data']['nodes']
        self.nodeids = [node['nodeid'] for node in nodes]
        self.contents = [node['content'] for node in nodes]

    async def post(self, url: str, **kwargs):
        resp = None
        async with httpx.AsyncClient() as client:
            for i in range(3):
                try:
                    resp = await client.post(url, timeout=60, **kwargs)
                    if resp:
                        break
                except:
                    logger.warning(f"Error in post {url}, retry {i}/3")
                    continue
        if not resp:
            raise NetworkError('网络错误')
        result = resp.json()
        if result['status'] == 0:
            return result
        elif result['status'] == -1:
            raise AccountError('账号不存在，请更换apikey！')
        elif result['status'] == -6:
            raise AccountError('账号已被封禁，请更换apikey！')
        elif result['status'] == -5:
            raise ContentError(
                "存在不和谐内容，类型：{}，剩余血量：{}".format(
                    result['data']['label'],
                    result['data']['total_count']-result['data']['shut_count']
                )
            )
        else:
            raise CaiyunError(result['msg'])
