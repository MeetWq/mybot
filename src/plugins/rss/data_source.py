import httpx
import feedparser
from urllib.parse import quote
from typing import List
from nonebot import get_driver
from nonebot.log import logger

from .rss_class import RSS

global_config = get_driver().config
httpx_proxy = {
    'http://': global_config.http_proxy,
    'https://': global_config.http_proxy
}


async def get_rss_info(url: str) -> dict:
    try:
        async with httpx.AsyncClient(proxies=httpx_proxy) as client:
            resp = await client.get(url, timeout=20)
            result = resp.text
        return feedparser.parse(result)
    except:
        return {}


async def update_rss_info(rss: RSS) -> bool:
    info = await get_rss_info(rss.url)
    if not info:
        return False
    try:
        rss.title = info['feed']['title']
        rss.link = info['feed']['link']
    except:
        return False
    try:
        rss.logo = info['feed']['image']['href']
    except:
        rss.logo = f'https://ui-avatars.com/api/?background=random&name={quote(rss.title)}'
    try:
        rss.rights = info['feed']['rights']
    except:
        pass
    return True


async def update_rss(rss: RSS) -> List[dict]:
    info = await get_rss_info(rss.url)
    if not info:
        return []
    new_entries = []
    entries = info.get('entries')
    if not entries:
        return []
    for entry in entries[::-1]:
        try:
            time = RSS.parse_time(entry['published_parsed'])
            if time <= rss.last_update:
                continue
            title = entry['title']
            summary = entry['summary']
            link = entry['link']
            authors = []
            tags = []
            try:
                for author in entry['authors']:
                    authors.append(author['name'])
                for tag in entry['tags']:
                    tags.append(tag['term'])
            except:
                pass
            new_entries.append({
                'time': time.strftime('%c'),
                'title': title,
                'summary': summary,
                'link': link,
                'author': ', '.join(authors),
                'tags': ', '.join(tags)
            })
        except:
            continue
    try:
        newest_time = RSS.parse_time(entries[0]['published_parsed'])
        if newest_time > rss.last_update:
            rss.last_update = newest_time
    except:
        rss.last_update = RSS.time_now()
    if new_entries:
        logger.debug(f'new rss in {rss.name}:')
        logger.debug(new_entries)
    return new_entries
