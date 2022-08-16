import random
from pathlib import Path
from typing import Optional

image_path = Path() / "data" / "picbank" / "images"


def get_random_pic(name: str) -> Optional[Path]:
    bank_path = image_path / name
    if not bank_path.exists():
        return None
    pics = [
        f
        for f in bank_path.iterdir()
        if f.is_file() and f.suffix in [".jpg", ".png", ".gif"]
    ]
    if not pics:
        return None
    return random.choice(pics)
