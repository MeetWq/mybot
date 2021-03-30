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


async def get_cp_story(name_a, name_b):
    try:
        browser = await launch({'args': ['--no-sandbox']}, headless=True)
        page = await browser.newPage()
        await page.goto('https://mxh-mini-apps.github.io/mxh-cp-stories/')
        await page.focus('input[type=text][id=gong-fang]')
        await page.keyboard.type(name_a)
        await page.focus('input[type=text][id=shou-fang]')
        await page.keyboard.type(name_b)
        await page.evaluate('function() {document.querySelector("button[id=write-story]").click()}')
        story_p = await page.querySelector('p[id=story]')
        story = await (await story_p.getProperty('textContent')).jsonValue()
        await browser.close()
        return story
    except (AttributeError, TypeError, OSError, NetworkError):
        logger.debug(traceback.format_exc())
        return ''


async def get_cxh(text):
    try:
        browser = await launch({'args': ['--no-sandbox', '--ignore-certificate-errors', '--ignore-certificate-errors-spki-list', '--enable-features=NetworkService']}, headless=True)
        page = await browser.newPage()
        await page.goto('https://cxh.papapoi.com/')
        await page.evaluate(f'function() {{document.querySelector("input[type=text][id=rawText]").value = "{text}"}}')
        await page.evaluate('function() {document.querySelector("button[id=create]").click()}')
        result_input = await page.querySelector('input[type=text][id=resultText]')
        result = await (await result_input.getProperty('value')).jsonValue()
        await browser.close()
        return result
    except (AttributeError, TypeError, OSError, NetworkError):
        logger.debug(traceback.format_exc())
        return ''
