"""Example data model classes using [Pydantic](https://pydantic-docs.helpmanual.io/)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Adventurer(BaseModel):
    """A person often late for dinner but with a tale or two to tell."""

    name: str
    profession: str
    level: int
    affinity: str


class QuestGiver(BaseModel):
    """A person who offers a task that needs completing."""

    name: str
    faction: Optional[str]
    location: str


class Quest(BaseModel):
    """A task to complete, with some monetary reward."""

    name: str
    giver: QuestGiver
    reward_gold: int


class Party(BaseModel):
    """A group of adventurers finding themselves doing and saying things altogether unexpected."""

    name: str
    formed_datetime: datetime
    members: List[Adventurer]
    active_quest: Optional[Quest]
