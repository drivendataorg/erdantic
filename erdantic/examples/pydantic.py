"""Example data model classes using [Pydantic](https://pydantic-docs.helpmanual.io/)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Adventurer(BaseModel):
    name: str
    profession: str
    level: int
    affinity: str


class QuestGiver(BaseModel):
    name: str
    faction: Optional[str]
    location: str


class Quest(BaseModel):
    name: str
    giver: QuestGiver
    reward_gold: int


class Party(BaseModel):
    name: str
    formed_datetime: datetime
    members: List[Adventurer]
    active_quest: Optional[Quest]
