import json
from pathlib import Path
from typing import List, Dict

from .property import Property
from .event import WeightedEvent


class AgeManager:
    def __init__(self, prop: Property):
        self.prop = prop
        age_path: Path = Path(__file__).parent / 'resources/age.json'
        age_data: dict = json.load(age_path.open('r', encoding='utf8'))
        self.ages: Dict[int, List[WeightedEvent]] = \
            {int(k): [WeightedEvent(s) for s in v.get('event', [])]
             for k, v in age_data.items()}

    def get_events(self) -> List[WeightedEvent]:
        return self.ages[self.prop.AGE]

    def grow(self):
        self.prop.AGE += 1
