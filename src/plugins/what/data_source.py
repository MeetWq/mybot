import re
import aiohttp
import traceback
from fuzzywuzzy import fuzz, process
from bs4 import BeautifulSoup
from urllib.parse import quote
from nonebot.log import logger
from nonebot.adapters.cqhttp import Message, MessageSegment

import wikipedia
from wikipedia import WikipediaException
from baike import getBaike

wikipedia.set_lang('zh')


async def get_content(keyword, source='all', force=False):
    try:
        msg = ''
        if source in sources:
            title, msg = await sources[source](keyword, force)
        elif source == 'all':
            titles = []
            msgs = []
            for s in sources:
                t, m = await sources[s](keyword, force)
                titles.append(t)
                msgs.append(m)
            title = process.extractOne(keyword, titles)[0]
            index = titles.index(title)
            msg = msgs[index]
        return msg
    except:
        logger.warning('Error in get content: ' + traceback.format_exc())
        return ''


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


async def get_wiki(keyword, force=False):
    entries = wikipedia.search(keyword)
    if len(entries) < 1:
        return '', ''
    title = entries[0]
    if not force:
        if fuzz.ratio(title, keyword) < 90:
            return '', ''

    content = wikipedia.summary(title)
    msg = title + ':\n---------------\n' + content
    return title, msg


sources = {
    'nbnhhsh': get_nbnhhsh,
    'jiki': get_jiki,
    'baidu': get_baidu,
    'wiki': get_wiki
}
