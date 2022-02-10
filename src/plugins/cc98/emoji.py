from pathlib import Path
from typing import Optional

dir_path = Path(__file__).parent
emoji_path = dir_path / "resources"

emoji_list = {
    "emoji_ac": {"pattern": r"^(&#91;)?ac\d{2,4}(&#93;)?$", "dirname": "ac"},
    "emoji_em": {"pattern": r"^(&#91;)?em\d{2}(&#93;)?$", "dirname": "em"},
    "emoji_mahjong": {
        "pattern": r"^(&#91;)?[acf]:?\d{3}(&#93;)?$",
        "dirname": "mahjong",
    },
    "emoji_ms": {"pattern": r"^(&#91;)?ms\d{2}(&#93;)?$", "dirname": "ms"},
    "emoji_tb": {"pattern": r"^(&#91;)?tb\d{2}(&#93;)?$", "dirname": "tb"},
    "emoji_cc98": {"pattern": r"^(&#91;)?[Cc][Cc]98\d{2}(&#93;)?$", "dirname": "cc98"},
}


def get_emoji(dirname: str, filename: str) -> Optional[bytes]:
    filename = filename.strip().split(".")[0].replace(":", "").lower()
    exts = [".jpg", ".png", ".gif"]
    for ext in exts:
        filepath = emoji_path / dirname / (filename + ext)
        if filepath.exists():
            return filepath.read_bytes()
    return None
