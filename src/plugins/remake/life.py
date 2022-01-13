import itertools
from typing import List, Dict, Iterator

from .age import AgeManager
from .event import EventManager
from .property import Property
from .talent import Talent, TalentManager


class Life:
    def __init__(self):
        self.property: Property = Property(self)
        self.age: AgeManager = AgeManager(self.property)
        self.event: EventManager = EventManager(self.property)
        self.talent: TalentManager = TalentManager(self.property)

    def prefix(self) -> Iterator[str]:
        yield f'【{self.property.AGE}岁/颜{self.property.CHR}智{self.property.INT}体{self.property.STR}钱{self.property.MNY}乐{self.property.SPR}】'

    def alive(self) -> bool:
        return self.property.LIF > 0

    def run(self) -> Iterator[List[str]]:
        while self.alive():
            self.age.grow()
            talent_log = self.talent.update_talent()
            event_log = self.event.run_events(self.age.get_events())
            yield list(itertools.chain(self.prefix(), event_log, talent_log))

    def rand_talents(self, num: int) -> List[Talent]:
        return list(self.talent.rand_talents(num))

    def set_talents(self, talents: List[Talent]):
        for t in talents:
            self.talent.add_talent(t)

    def apply_property(self, effect: Dict[str, int]):
        self.property.apply(effect)

    def gen_summary(self) -> str:
        return self.property.gen_summary()
