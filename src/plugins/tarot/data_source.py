import json
import random
from io import BytesIO
from pathlib import Path
from typing import Tuple

from PIL import Image

dir_path = Path(__file__).parent
tarot_path = dir_path / "resources"
image_path = tarot_path / "images"


async def get_tarot() -> Tuple[BytesIO, str]:
    card = get_random_tarot()
    reverse = random.choice([False, True])
    filename = "{}{:02d}.jpg".format(card["type"], card["num"])
    image = Image.open(image_path / filename)
    if reverse:
        image = image.rotate(180)
    content = (
        f"{card['name']} ({card['name-en']}) {'逆位' if reverse else '正位'}\n"
        f"牌意：{card['meaning']['reverse' if reverse else 'normal']}"
    )
    output = BytesIO()
    image.save(output, format="jpeg")
    return output, content


def get_random_tarot() -> dict:
    path = tarot_path / "tarot.json"
    with path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    types = ["major", "pentacles", "wands", "cups", "swords"]
    cards = []
    for type in types:
        cards.extend(data[type])
    return random.choice(cards)
