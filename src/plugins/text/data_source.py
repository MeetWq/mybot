import traceback
from nonebot.log import logger
from src.libs.playwright import get_new_page


async def get_text(text, type=0):
    try:
        if type == 0:
            result = await get_cxh_text(text)
        elif type == 1:
            result = await get_mars_text(text)
        elif type == 2:
            result = await get_ant_text(text)
        elif type == 3:
            result = await get_invert_text(text)
        elif type == 4:
            result = await get_bug_text(text)
        return result
    except (AttributeError, TypeError, OSError):
        logger.debug(traceback.format_exc())
        return ''


async def get_cxh_text(text):
    async with get_new_page() as page:
        await page.goto('http://www.atoolbox.net/Tool.php?Id=864')
        await page.evaluate(f'function() {{document.querySelector("input[type=text][id=rawText]").value = "{text}"}}')
        await page.evaluate('function() {document.querySelector("button[id=create]").click()}')
        result = await page.query_selector('input[type=text][id=resultText]')
        result_text = await (await result.get_property('value')).json_value()
        return result_text


async def get_mars_text(text):
    async with get_new_page() as page:
        await page.goto('http://www.atoolbox.net/Tool.php?Id=820')
        await page.evaluate(f'function() {{document.querySelector("textarea[id=en-message]").value = "{text}"}}')
        await page.evaluate('function() {document.querySelector("button[id=btn-encode]").click()}')
        result = await page.query_selector('textarea[id=en-output]')
        result_text = await (await result.get_property('value')).json_value()
        return result_text


async def get_ant_text(text):
    async with get_new_page() as page:
        await page.goto('http://www.atoolbox.net/Tool.php?Id=822')
        await page.evaluate(f'function() {{document.querySelector("textarea[id=en-message]").value = "{text}"}}')
        await page.evaluate('function() {document.querySelector("button[id=btn-encode]").click()}')
        result = await page.query_selector('textarea[id=en-output]')
        result_text = await (await result.get_property('value')).json_value()
        return result_text


async def get_invert_text(text):
    async with get_new_page() as page:
        await page.goto('http://www.atoolbox.net/Tool.php?Id=759')
        await page.evaluate(f'function() {{document.querySelector("textarea[id=txtTitle]").value = "{text}"}}')
        await page.evaluate('function() {document.querySelector("button[id=btnFlip]").click()}')
        result = await page.query_selector('textarea[id=txtResult]')
        result_text = await (await result.get_property('value')).json_value()
        return result_text


async def get_bug_text(text):
    async with get_new_page() as page:
        await page.goto('http://www.atoolbox.net/Tool.php?Id=896')
        await page.evaluate(f'function() {{document.querySelector("textarea[id=input]").value = "{text}"}}')
        await page.evaluate('function() {document.querySelector("button[id=convert]").click()}')
        result = await page.query_selector('textarea[id=output]')
        result_text = await (await result.get_property('value')).json_value()
        return result_text
