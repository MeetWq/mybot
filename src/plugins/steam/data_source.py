import aiohttp
from bs4 import BeautifulSoup
from nonebot.adapters.cqhttp import Message, MessageSegment


async def get_steam_game(keyword: str) -> Message:
    url = f'https://steamstats.cn/api/steam/search?q={keyword}&page=1&format=json&lang=zh-hans'
    headers = {
        'referer': 'https://steamstats.cn/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.121 Safari/537.36 '
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            result = await resp.json()

    if len(result['data']['results']) == 0:
        return f'{keyword} 未搜索到结果！'
    else:
        data = result['data']['results'][0]
        app_id = data['app_id']
        name = data['name']
        cn_name = data['name_cn']
        avatar = data['avatar']
        description = await get_steam_game_description(app_id)

        message = Message()
        message.append(MessageSegment.image(file=avatar))
        info = f'\n{cn_name}\n{name}\nid: {app_id}\n\n'
        info += f'{description}' if description else ''
        message.append(info)
        return message


async def get_steam_game_description(game_id: int) -> str:
    url = f'https://store.steampowered.com/app/{game_id}/'
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            text = await resp.text()
    resp_bs4 = BeautifulSoup(text, 'lxml')
    description = resp_bs4.find('div', {'class': 'game_description_snippet'})
    if description:
        description = description.text
        return description.strip()
    return ''
