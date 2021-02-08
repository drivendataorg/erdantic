"""Example data model classes using standard library's
[`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class AlignmentLC(str, Enum):
    LAWFUL = "lawful"
    NEUTRAL = "neutral"
    CHAOTIC = "chaotic"


class AlignmentGE(str, Enum):
    GOOD = "good"
    NEUTRAL = "neutral"
    EVIL = "evil"


@dataclass
class Adventurer:
    """A person often late for dinner but with a tale or two to tell.

    Attributes:
        name (str): Name of this adventurer
        profession (str): Profession of this adventurer
        level (int): Level of this adventurer
        alignment (int): Alignment of this adventurer
    """

    name: str
    profession: str
    level: int
    alignment_lc: AlignmentLC
    alignment_ge: AlignmentGE


@dataclass
class QuestGiver:
    """A person who offers a task that needs completing.

    Attributes:
        name (str): Name of this quest giver
        faction (str): Faction that this quest giver belongs to
        location (str): Location this quest giver can be found
    """

    name: str
    faction: Optional[str]
    location: str


@dataclass
class Quest:
    """A task to complete, with some monetary reward.

    Attributes:
        name (str): Name by which this quest is referred to
        giver (QuestGiver): Person who offered the quest
        reward_gold (int): Amount of gold to be rewarded for quest completion
    """

    name: str
    giver: QuestGiver
    reward_gold: int


@dataclass
class Party:
    """A group of adventurers finding themselves doing and saying things altogether unexpected.

    Attributes:
        name (str): Name that party is known by
        formed_datetime (datetime): Timestamp of when the party was formed
        members (List[Adventurer]): Adventurers that belong to this party
        active_quest (Optional[Quest]): Current quest that party is actively tackling
    """

    name: str
    formed_datetime: datetime
    members: List[Adventurer]
    active_quest: Optional[Quest]
