import aiohttp
import datetime
from urllib.parse import quote
from nonebot.adapters.cqhttp import Message, MessageSegment


async def get_bangumi_info(keyword):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
    }
    url = f'https://api.bgm.tv/search/subject/{quote(keyword)}?type=2&responseGroup=Large&max_results=1'

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers) as resp:
            data = await resp.json()

    if 'code' in data.keys() and data['code'] == 404 or not data['list']:
        return f'番剧 {keyword} 未搜索到结果！'

    bangumi_id = data['list'][0]['id']
    url = f'https://api.bgm.tv/subject/{bangumi_id}?responseGroup=medium'

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers) as resp:
            data = await resp.json()

    name = data['name']
    cn_name = data['name_cn']
    summary = data['summary']
    img_url = data['images']['large']
    score = data['rating']['score']
    rating_total = data['rating']['total']
    air_date = data['air_date']
    air_weekday = data['air_weekday']
    weeks = ['一', '二', '三', '四', '五', '六', '日']
    week = weeks[int(air_weekday) - 1]

    message = Message()
    message.append(MessageSegment.image(file=img_url))
    info = f'\n{cn_name}\n{name}\n\n'
    info += f'{summary}\n\n' if summary else ''
    info += f'放送开始: {air_date}\n'
    info += f'放送星期: 周{week}\n'
    info += f'bangumi评分: {score} ({rating_total}人投票)'
    message.append(info)
    return message


async def get_new_bangumi():
    formatted_bangumi_data = await get_formatted_new_bangumi_json()
    new_bangumi_list = []
    now = datetime.datetime.now()
    for index in range(7):
        info = now.strftime('%m-%d') + ' 即将播出：'
        for data in formatted_bangumi_data[index]:
            info += '\n{} {} {}'.format(data['pub_time'], data['title'], data['pub_index'])
        new_bangumi_list.append(info)
        now += datetime.timedelta(days=1)
    return new_bangumi_list


async def get_new_bangumi_json():
    url = 'https://bangumi.bilibili.com/web_api/timeline_global'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://www.bilibili.com',
        'referer': 'https://www.bilibili.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers) as resp:
            result = await resp.json()
    return result


async def get_formatted_new_bangumi_json():
    all_bangumi_data = await get_new_bangumi_json()
    all_bangumi_data = all_bangumi_data['result'][-7:]
    formatted_bangumi_data = list()

    for bangumi_data in all_bangumi_data:
        temp_bangumi_data_list = list()
        for data in bangumi_data['seasons']:
            temp_bangumi_data_dict = dict()
            temp_bangumi_data_dict['title'] = data['title']
            temp_bangumi_data_dict['cover'] = data['cover']
            temp_bangumi_data_dict['pub_index'] = data['pub_index']
            temp_bangumi_data_dict['pub_time'] = data['pub_time']
            temp_bangumi_data_dict['url'] = data['url']
            temp_bangumi_data_list.append(temp_bangumi_data_dict)
        formatted_bangumi_data.append(temp_bangumi_data_list)
    return formatted_bangumi_data
