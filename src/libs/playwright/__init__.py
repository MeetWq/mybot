from typing import Generator
from contextlib import asynccontextmanager

from playwright.async_api import async_playwright, Browser, Page


async def get_browser(**kwargs) -> Browser:
    playwright = await async_playwright().start()
    return await playwright.chromium.launch(**kwargs)


@asynccontextmanager
async def get_new_page(**kwargs) -> Generator[Page, None, None]:
    browser = await get_browser(args=['--no-sandbox', '--disable-setuid-sandbox', '--single-process'])
    page = await browser.new_page(**kwargs)
    try:
        yield page
    finally:
        await page.close()
        await browser.close()
