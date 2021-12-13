import httpx
from typing import List
from nonebot import get_driver

from .config import Config

global_config = get_driver().config
caiyun_config = Config(**global_config.dict())
token = caiyun_config.caiyunai_apikey

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


async def post(url: str, **kwargs):
    resp = None
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.post(url, timeout=60, **kwargs)
                if resp:
                    break
            except:
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
            f"存在不和谐内容，类型：{result['data']['label']}，\
                剩余血量：{result['data']['total_count']-result['data']['shut_count']}")
    else:
        raise CaiyunError(result['msg'])


async def novel_save(content: str) -> dict:
    url = f'http://if.caiyunai.com/v2/novel/{token}/novel_save'
    params = {
        'content': content,
        'title': '',
        'ostype': ''
    }
    result = await post(url, json=params)
    data = result['data']
    return {
        'nid': data['nid'],
        'branchid': data['novel']['branchid'],
        'firstnode': data['novel']['firstnode']
    }


async def novel_ai(content: str, nid: str, branchid: str, lastnode: str,
                   model: str = '小梦0号') -> List[dict]:
    url = f'http://if.caiyunai.com/v2/novel/{token}/novel_ai'
    params = {
        'nid': nid,
        'content': content,
        'uid': token,
        'mid': model_list[model]['id'],
        'title': '',
        'ostype': '',
        'status': 'http',
        'lang': 'zh',
        'branchid': branchid,
        'lastnode': lastnode
    }
    result = await post(url, json=params)
    nodes = result['data']['nodes']
    return [{
            'nodeid': node['nodeid'],
            'content': node['content']
            } for node in nodes]


async def add_node(content: str, nid: str, nodeid: str, nodeids: List[str]):
    url = f'http://if.caiyunai.com/v2/novel/{token}/add_node'
    params = {
        'nodeids': nodeids,
        'choose': nodeid,
        'nid': nid,
        'value': content,
        'ostype': '',
        'lang': 'zh'
    }
    await post(url, json=params)


async def get_contents(state: dict, first=False):
    if first:
        novel = await novel_save(state['content'])
        state['model'] = '小梦0号'
        state['nid'] = novel['nid']
        state['branchid'] = novel['branchid']
        state['result'] = ''
        state['nodeid'] = novel['firstnode']
        state['nodeids'] = [state['nodeid']]

    await add_node(state['content'], state['nid'], state['nodeid'], state['nodeids'])
    state['result'] = state['result'] + state['content']
    nodes = await novel_ai(state['result'], state['nid'], state['branchid'],
                           state['nodeid'], state['model'])
    state['nodeids'] = [node['nodeid'] for node in nodes]
    state['contents'] = [node['content'] for node in nodes]
