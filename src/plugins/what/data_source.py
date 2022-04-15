import re
import httpx
from lxml import etree
from thefuzz import fuzz
from baike import getBaike
from typing import List, Tuple, Union
from urllib.parse import quote
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment


async def get_nbnhhsh(keyword: str) -> Tuple[str, str]:
    url = "https://lab.magiconch.com/api/nbnhhsh/guess"
    headers = {"referer": "https://lab.magiconch.com/nbnhhsh/"}
    data = {"text": keyword}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url=url, headers=headers, data=data)
        res = resp.json()
    title = ""
    result = []
    for i in res:
        if "trans" in i:
            if i["trans"]:
                title = i["name"]
                result.append(f"{i['name']} => {'，'.join(i['trans'])}")
    result = "\n".join(result)
    if fuzz.ratio(title.lower(), keyword.lower()) < 90:
        return "", ""
    return title, result


async def get_jiki(keyword: str) -> Tuple[str, Union[str, Message]]:
    search_url = "https://jikipedia.com/search?phrase={}".format(quote(keyword))
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=search_url)
        result = resp.text

    if "对不起！小鸡词典暂未收录该词条" in result:
        return "", ""

    dom = etree.HTML(result, etree.HTMLParser())
    card_urls = dom.xpath(
        "//div[contains(@class, 'masonry')]/div/div/div/a[contains(@class, 'title-container')]/@href"
    )
    if not card_urls:
        return "", ""

    card_url = card_urls[0]
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=card_url)
        result = resp.text

    dom = etree.HTML(result, etree.HTMLParser())
    title = dom.xpath(
        "//div[@class='section card-middle']/div[@class='title-container']/div/h1/text()"
    )[0]
    content = dom.xpath(
        "//div[@class='section card-middle']/div[@class='content']/div"
    )[0]
    content = content.xpath("string(.)").strip()
    img_urls = dom.xpath(
        "//div[@class='section card-middle']/div/div/div[@class='show-images']/img/@src"
    )
    if fuzz.ratio(str(title).lower(), keyword.lower()) < 90:
        return "", ""

    msg = Message()
    msg.append(title + ":\n---------------\n")
    msg.append(content)
    for img_url in img_urls:
        msg.append(MessageSegment.image(file=img_url))
    return title, msg


async def get_baidu(keyword: str) -> Tuple[str, str]:
    content = getBaike(keyword)
    if not content:
        return "", ""

    match_obj = re.match(r"(.*?)(（.*?）?)\n(.*)", content)
    if not match_obj:
        return "", ""

    title = match_obj.group(1)
    subtitle = match_obj.group(2)
    text = match_obj.group(3)
    if fuzz.ratio(title.lower(), keyword.lower()) < 90:
        return "", ""

    msg = title
    if subtitle:
        msg += subtitle
    msg += ":\n---------------\n" + text
    return title, msg


sources_func = {"jiki": get_jiki, "baidu": get_baidu, "nbnhhsh": get_nbnhhsh}


async def get_content(
    keyword: str, sources=["jiki", "baidu", "nbnhhsh"]
) -> Union[str, Message]:
    result = ""
    msgs: List[Tuple[str, Union[str, Message]]] = []
    for s in sources:
        try:
            title, msg = await sources_func[s](keyword)
            if title and msg:
                msgs.append((title, msg))
        except Exception as e:
            logger.warning(f"Error in get_content({keyword}) using {s}: {e}")

    if len(msgs) == 1:
        result = msgs[0][1]
    elif len(msgs) > 1:
        msgs = sorted(
            msgs, key=lambda m: fuzz.ratio(m[0].lower(), keyword.lower()), reverse=True
        )
        result = msgs[0][1]
    return result
