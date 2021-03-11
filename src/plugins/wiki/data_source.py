import wikipedia
from wikipedia import WikipediaException
from fuzzywuzzy import fuzz
import traceback
from nonebot.log import logger

wikipedia.set_lang("zh")


async def get_content(keyword):
    try:
        entries = wikipedia.search(keyword)
        if len(entries) < 1:
            return '', ''
        title = entries[0]
        score = fuzz.ratio(title, keyword)
        if score > 80:
            return title, wikipedia.summary(title)
        else:
            return '', ''
    except WikipediaException:
        logger.warning('Error in get content: ' + traceback.format_exc())
        return '', ''
