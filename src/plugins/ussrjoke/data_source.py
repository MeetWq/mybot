import traceback
from pyppeteer import launch
from pyppeteer.chromium_downloader import check_chromium, download_chromium
from pyppeteer.errors import NetworkError
from nonebot.log import logger

if not check_chromium():
    download_chromium()


async def get_ussrjoke(thing, man, theory, victim, range):
    try:
        browser = await launch({'args': ['--no-sandbox']}, headless=True)
        page = await browser.newPage()
        await page.goto('https://namespacexp.github.io/joke/')
        await page.evaluate('function() {{document.querySelector("input[type=text][id=mthing]").value = "{}"}}'.format(thing))
        await page.evaluate('function() {{document.querySelector("input[type=text][id=mman]").value = "{}"}}'.format(man))
        await page.evaluate('function() {{document.querySelector("input[type=text][id=mtheory]").value = "{}"}}'.format(theory))
        await page.evaluate('function() {{document.querySelector("input[type=text][id=mvictim]").value = "{}"}}'.format(victim))
        await page.evaluate('function() {{document.querySelector("input[type=text][id=mrange]").value = "{}"}}'.format(range))
        await page.evaluate('function() {document.querySelector("button[type=button][id=mgo]").click()}')
        joke_div = await page.querySelector('div[id=mjoke]')
        joke = await (await joke_div.getProperty('textContent')).jsonValue()
        await browser.close()
        return joke
    except (AttributeError, TypeError, OSError, NetworkError):
        logger.debug(traceback.format_exc())
        return ''
