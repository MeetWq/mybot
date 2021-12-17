import json
import random
from pathlib import Path
from typing import Dict, List, Set, Iterator

from .property import Property
from .utils import parse_condition


class Talent:
    def __init__(self, data):
        self.id: int = int(data['id'])
        self.name: str = data['name']
        self.description: str = data['description']
        self.grade: int = int(data['grade'])
        self.exclusive: List[int] = [int(x) for x in data['exclusive']] \
            if 'exclusive' in data else []
        self.effect: Dict[str, int] = data['effect'] \
            if 'effect' in data else {}
        self.status = int(data['status']) if 'status' in data else 0
        self.condition = parse_condition(data['condition']) \
            if 'condition' in data else lambda _: True

    def __str__(self) -> str:
        return f'{self.name}（{self.description}）'

    def exclusive_with(self, talent) -> bool:
        return talent.id in self.exclusive or self.id in talent.exclusive

    def check_condition(self, prop: Property) -> bool:
        return self.condition(prop)

    def run(self, prop: Property) -> List[str]:
        if self.check_condition(prop):
            prop.apply(self.effect)
            return [f'天赋【{self.name}】发动：{self.description}']
        return []


grade_count = 4
grade_prob = [0.889, 0.1, 0.01, 0.001]
talent_path: Path = Path(__file__).parent / 'resources/talents.json'
talent_data: dict = json.load(talent_path.open('r', encoding='utf8'))
talent_list: List[Talent] = [Talent(data) for data in talent_data.values()]
talent_dict: Dict[int, List[Talent]] = \
    {i: [t for t in talent_list if t.grade == i] for i in range(grade_count)}


class TalentManager:

    def __init__(self, prop: Property):
        self.prop = prop
        self.talents: List[Talent] = []
        self.triggered: Set[int] = set()

    @staticmethod
    def rand_talents(count: int) -> Iterator[Talent]:
        def rand_grade():
            rnd = random.random()
            result = grade_count
            while rnd > 0:
                result -= 1
                rnd -= grade_prob[result]
            return result

        counts = dict([(i, 0) for i in range(grade_count)])
        for _ in range(count):
            counts[rand_grade()] += 1
        for grade in range(grade_count - 1, -1, -1):
            count = counts[grade]
            n = len(talent_dict[grade])
            if count > n:
                counts[grade - 1] += count - n
                count = n
            for talent in random.sample(talent_dict[grade], k=count):
                yield talent

    def update_talent(self) -> Iterator[str]:
        for t in self.talents:
            if t.id in self.triggered:
                continue
            for result in t.run(self.prop):
                self.triggered.add(t.id)
                yield result

    def add_talent(self, talent: Talent):
        for t in self.talents:
            if t.id == talent.id:
                return
        self.talents.append(talent)
