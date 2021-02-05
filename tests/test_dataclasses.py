from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from erdantic import create_erd


@dataclass
class Adventurer:
    name: str
    profession: str
    level: int
    affinity: str


@dataclass
class QuestGiver:
    name: str
    faction: Optional[str]
    location: str


@dataclass
class Quest:
    name: str
    giver: QuestGiver
    reward_gold: int


@dataclass
class Party:
    name: str
    formed_datetime: datetime
    members: List[Adventurer]
    active_quest: Optional[Quest]


def test_model_crawling():
    diagram = create_erd(Party)
    assert {m.dataclass for m in diagram.models} == {Party, Adventurer, Quest, QuestGiver}
