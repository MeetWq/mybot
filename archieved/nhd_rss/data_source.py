import re
from dataclasses import dataclass
from datetime import datetime

import dateparser
import httpx
from lxml import etree
from nonebot.log import logger

from .config import rss_config


@dataclass
class NHDRSSEntry:
    title: str
    subtitle: str
    size: str
    author: str
    category: str
    pubDate: datetime


async def get_rss_entries() -> list[NHDRSSEntry]:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(rss_config.nhd_rss_url, timeout=20)
            content = resp.content
    except Exception as e:
        logger.warning(f"Error in get_rss_entries: {e}")
        return []
    root = etree.HTML(content, etree.XMLParser())
    items = root.xpath("//item")

    entries = []
    for item in items:
        try:
            raw_title = str(item.xpath("./title/text()")[0])
            raw_title, size, _ = re.split(
                r"\[(\d{1,4}\.\d{2} [KMGTP]B)\]$", raw_title, maxsplit=1
            )
            title, subtitle, _ = re.split(r"\[(.*)\]$", raw_title, maxsplit=1)
            author = str(item.xpath("./author/text()")[0]).split("@")[0]
            category = str(item.xpath("./category/text()")[0])
            pubDate = dateparser.parse(str(item.xpath("./pubDate/text()")[0]))
            if not pubDate:
                continue
            entries.append(
                NHDRSSEntry(
                    title=title,
                    subtitle=subtitle,
                    size=size,
                    author=author,
                    category=category,
                    pubDate=pubDate,
                )
            )
        except Exception as e:
            logger.warning(f"RSS item parse failed: {e}")
            pass
    return entries
