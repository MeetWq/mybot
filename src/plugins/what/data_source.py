import re
import aiohttp
import traceback
from fuzzywuzzy import fuzz, process
from bs4 import BeautifulSoup
from urllib.parse import quote
from nonebot.log import logger
from nonebot.adapters.cqhttp import Message, MessageSegment

from baike import getBaike


async def get_content(keyword, source='all', force=False, less=False):
    msg = ''
    if source in sources:
        try:
            title, msg = await sources[source](keyword, force)
        except:
            logger.warning(f'Error in get {source} content: \n{traceback.format_exc()}')
    elif source == 'all':
        titles = []
        msgs = []
        sources_used = sources_less if less else sources
        for s in sources_used.keys():
            try:
                t, m = await sources_used[s](keyword, force)
                if t and m:
                    titles.append(t)
                    msgs.append(m)
            except:
                logger.warning(f'Error in get {s} content: \n{traceback.format_exc()}')
        if msgs:
            title = process.extractOne(keyword, titles)[0]
            index = titles.index(title)
            msg = msgs[index]
    return msg


async def get_nbnhhsh(keyword, force=False):
    url = 'https://lab.magiconch.com/api/nbnhhsh/guess'
    headers = {
        'referer': 'https://lab.magiconch.com/nbnhhsh/'
    }
    data = {
        'text': keyword
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=data) as resp:
            res = await resp.json()
    title = ''
    result = ''
    for i in res:
        if 'trans' in i:
            if i['trans']:
                title = i['name']
                result += f"{i['name']} => {'，'.join(i['trans'])}"
        elif force:
            if i['inputting']:
                title = i['name']
                result += f"{i['name']} => {'，'.join(i['inputting'])}"
    if not force:
        if fuzz.ratio(title, keyword) < 90:
            return '', ''
    return title, result


async def get_jiki(keyword, force=False):
    keyword = quote(keyword)
    search_url = 'https://jikipedia.com/search?phrase={}'.format(keyword)
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as resp:
            result = await resp.text()

    if (not force and '对不起！小鸡词典暂未收录该词条' in result) or \
            (force and '你可能喜欢的词条' not in result):
        return '', ''

    search_result = BeautifulSoup(result, 'lxml')
    masonry = search_result.find('div', {'class': 'masonry'})
    if not masonry:
        return '', ''

    card = masonry.find('div', recursive=False)
    card_content = card.find('a', {'class': 'card-content'})
    if not card_content:
        return '', ''
    card_url = 'https://jikipedia.com' + card_content.get('href')
    async with aiohttp.ClientSession() as session:
        async with session.get(card_url) as resp:
            result = await resp.text()

    card_result = BeautifulSoup(result, 'lxml')
    card_section = card_result.find('div', {'class': 'section card-middle'})
    title = card_section.find('div', {'class': 'title-container'}).find('span', {'class': 'title'}).text
    content = card_section.find('div', {'class': 'content'}).text
    images = card_section.find_all('div', {'class': 'show-images'})
    img_urls = []
    for image in images:
        img_urls.append(image.find('img').get('src'))

    msg = Message()
    msg.append(title + ':\n---------------\n')
    msg.append(content)
    for img_url in img_urls:
        msg.append(MessageSegment.image(file=img_url))
    return title, msg


async def get_baidu(keyword, force=False):
    content = getBaike(keyword)
    if not content.strip():
        return '', ''
    match_obj = re.match(r'(.*?)(（.*?）)?\n(.*)', content)
    if not match_obj:
        return '', ''
    title = match_obj.group(1)
    subtitle = match_obj.group(2)
    text = match_obj.group(3)
    if not force:
        if fuzz.ratio(title, keyword) < 90:
            return '', ''

    msg = title
    if subtitle:
        msg += subtitle
    msg += ':\n---------------\n' + text
    return title, msg


sources = {
    'nbnhhsh': get_nbnhhsh,
    'jiki': get_jiki,
    'baidu': get_baidu
}

sources_less = {
    'nbnhhsh': sources['nbnhhsh'],
    'jiki': sources['jiki']
}
