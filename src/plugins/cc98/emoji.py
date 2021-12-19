from pathlib import Path

dir_path = Path(__file__).parent
emoji_path = dir_path / 'resources'

emoji_list = {
    'emoji_ac': {
        'pattern': r'^(&#91;)?ac\d{2,4}(&#93;)?$',
        'dir_name': 'ac'
    },
    'emoji_em': {
        'pattern': r'^(&#91;)?em\d{2}(&#93;)?$',
        'dir_name': 'em'
    },
    'emoji_mahjong': {
        'pattern': r'^(&#91;)?[acf]:?\d{3}(&#93;)?$',
        'dir_name': 'mahjong'
    },
    'emoji_ms': {
        'pattern': r'^(&#91;)?ms\d{2}(&#93;)?$',
        'dir_name': 'ms'
    },
    'emoji_tb': {
        'pattern': r'^(&#91;)?tb\d{2}(&#93;)?$',
        'dir_name': 'tb'
    },
    'emoji_cc98': {
        'pattern': r'^(&#91;)?[Cc][Cc]98\d{2}(&#93;)?$',
        'dir_name': 'cc98'
    }
}


def get_emoji(dir_name: str, file_name: str) -> bytes:
    file_name = file_name.strip().split('.')[0].replace(':', '').lower()
    file_ext = ['.jpg', '.png', '.gif']
    for ext in file_ext:
        file_path = emoji_path / dir_name / (file_name + ext)
        if file_path.exists():
            return file_path.read_bytes()
    return None
