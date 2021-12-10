import re
import httpx
import traceback
from lxml import etree
from thefuzz import fuzz
from urllib.parse import quote
from nonebot.log import logger
from nonebot.adapters.cqhttp import Message, MessageSegment

from baike import getBaike


async def get_content(keyword, source='all', force=False, less=False):
    msg = ''
    if source in sources:
        try:
            _, msg = await sources[source](keyword, force)
        except:
            logger.warning(
                f'Error in get {source} content: \n{traceback.format_exc()}')
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
                logger.warning(
                    f'Error in get {s} content: \n{traceback.format_exc()}')
        if msgs:
            index = 0
            max_ratio = 0
            for i in range(len(msgs)):
                ratio = fuzz.ratio(titles[i].lower(), keyword.lower())
                if ratio > max_ratio:
                    index = i
                    max_ratio = ratio
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
    async with httpx.AsyncClient() as client:
        resp = await client.post(url=url, headers=headers, data=data)
        res = resp.json()
    title = ''
    result = []
    for i in res:
        if 'trans' in i:
            if i['trans']:
                title = i['name']
                result.append(f"{i['name']} => {'，'.join(i['trans'])}")
        elif force:
            if i['inputting']:
                title = i['name']
                result.append(f"{i['name']} => {'，'.join(i['inputting'])}")
    result = '\n'.join(result)
    if not force:
        if fuzz.ratio(title, keyword) < 90:
            return '', ''
    return title, result


async def get_jiki(keyword, force=False):
    keyword = quote(keyword)
    search_url = 'https://jikipedia.com/search?phrase={}'.format(keyword)
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=search_url)
        result = resp.text

    if (not force and '对不起！小鸡词典暂未收录该词条' in result) or \
            (force and '你可能喜欢的词条' not in result):
        return '', ''

    dom = etree.HTML(result)
    card_urls = dom.xpath(
        "//div[@class='masonry']/div/a[@class='card-content']/@href")
    if not card_urls:
        return '', ''
    card_url = 'https://jikipedia.com' + card_urls[0]
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=card_url)
        result = resp.text

    dom = etree.HTML(result)
    title = dom.xpath(
        "//div[@class='section card-middle']/div[@class='title-container']/span[@class='title']/text()")[0]
    content = dom.xpath(
        "//div[@class='section card-middle']/div[@class='content']/text()")[0]
    img_urls = dom.xpath(
        "//div[@class='section card-middle']/div[@class='show-images']/img/@src")

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
    'jiki': get_jiki,
    'baidu': get_baidu,
    'nbnhhsh': get_nbnhhsh
}

sources_less = {
    'jiki': sources['jiki'],
    'nbnhhsh': sources['nbnhhsh']
}
