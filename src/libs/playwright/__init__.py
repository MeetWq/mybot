from typing import Optional, Generator
from contextlib import asynccontextmanager

from playwright.async_api import async_playwright, Browser, Page

_browser: Optional[Browser] = None


async def init(**kwargs) -> Browser:
    global _browser
    playwright = await async_playwright().start()
    _browser = await playwright.chromium.launch(**kwargs)
    return _browser


async def get_browser(**kwargs) -> Browser:
    if _browser and _browser.is_connected():
        return _browser
    else:
        return await init(**kwargs)


@asynccontextmanager
async def get_new_page(**kwargs) -> Generator[Page, None, None]:
    browser = await get_browser()
    page = await browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()
