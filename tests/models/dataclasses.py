from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


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
