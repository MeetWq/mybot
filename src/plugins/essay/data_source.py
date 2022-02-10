import re
import json
import httpx
import random
import traceback
from typing import List
from pathlib import Path
from nonebot.log import logger

dir_path = Path(__file__).parent
data_path = dir_path / "resources"


async def get_ussrjoke(thing, man, theory, victim, range) -> str:
    path = data_path / "ussr-jokes.json"
    with path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return random.choice(data["jokes"]).format(
        thing=thing, man=man, theory=theory, victim=victim, range=range
    )


async def get_cp_story(name_a, name_b) -> str:
    path = data_path / "cp-stories.json"
    with path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return random.choice(data["stories"]).format(A=name_a, B=name_b)


async def get_marketing_article(topic, description, another) -> str:
    path = data_path / "marketing-article.json"
    with path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return random.choice(data["text"]).format(
        topic=topic, description=description, another=another
    )


async def get_chicken_soup() -> str:
    path = data_path / "soups.json"
    with path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return random.choice(data["soups"])


async def get_head_poem(keyword: str) -> str:
    if not re.fullmatch(r"[\u4e00-\u9fa5]+", keyword):
        return "关键词只能是汉字哦"

    if len(keyword) > 12:
        return "关键词过长，最多为12个字"

    url = "http://api.yanxi520.cn/api/betan.php"
    params = {"b": random.choice([5, 7]), "a": 1, "msg": keyword}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, params=params)
        result = resp.text
    return result


commands = {
    "ussrjoke": {
        "aliases": {"苏联笑话"},
        "func": get_ussrjoke,
        "help": "苏联笑话 {要讽刺的事} {谁提出来的} {有助于什么} {针对的是谁} {起作用范围}",
        "arg_num": 5,
    },
    "cpstory": {
        "aliases": {"cp文", "CP文"},
        "func": get_cp_story,
        "help": "CP文 {人物A} {人物B}",
        "arg_num": 2,
    },
    "marketing": {
        "aliases": {"营销号"},
        "func": get_marketing_article,
        "help": "营销号 {主题} {描述} {另一种描述}",
        "arg_num": 3,
    },
    "chickensoup": {
        "aliases": {"毒鸡汤"},
        "func": get_chicken_soup,
        "help": "毒鸡汤",
        "arg_num": 0,
    },
    "headpoem": {
        "aliases": {"藏头诗"},
        "func": get_head_poem,
        "help": "藏头诗 {keyword}",
        "arg_num": 1,
    },
}


async def get_essay(type: str, texts: List[str]) -> str:
    try:
        func = commands[type]["func"]
        return await func(*texts)
    except:
        logger.warning(traceback.format_exc())
        return "出错了，请稍后再试"
