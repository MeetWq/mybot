import aiohttp
import feedparser
from urllib.parse import quote
from typing import List
from datetime import timedelta
from nonebot import get_driver

from .rss_class import RSS

global_config = get_driver().config
proxy = global_config.http_proxy


async def get_rss_info(url: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy) as resp:
                result = await resp.text()
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
            if time <= rss.last_update + timedelta(seconds=0.5):
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
        rss.last_update = RSS.parse_time(entries[0]['published_parsed'])
    except:
        rss.last_update = RSS.time_now()
    return new_entries
