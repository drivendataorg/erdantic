"""Example struct classes using [msgspec](https://jcristharif.com/msgspec/)."""

from datetime import datetime
from enum import Enum
from typing import Optional

import msgspec


class Alignment(str, Enum):
    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    TRUE_NEUTRAL = "true_neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"


class Adventurer(msgspec.Struct):
    """A person often late for dinner but with a tale or two to tell.

    Attributes:
        name (str): Name of this adventurer
        profession (str): Profession of this adventurer
        alignment (Alignment): Alignment of this adventurer
        level (int): Level of this adventurer
    """

    name: str
    profession: str
    alignment: Alignment
    level: int = 1


class QuestGiver(msgspec.Struct):
    """A person who offers a task that needs completing.

    Attributes:
        name (str): Name of this quest giver
        faction (str): Faction that this quest giver belongs to
        location (str): Location this quest giver can be found
    """

    name: str
    faction: Optional[str] = None
    location: str = "Adventurer's Guild"


class Quest(msgspec.Struct):
    """A task to complete, with some monetary reward.

    Attributes:
        name (str): Name by which this quest is referred to
        giver (QuestGiver): Person who offered the quest
        reward_gold (int): Amount of gold to be rewarded for quest completion
    """

    name: str
    giver: QuestGiver
    reward_gold: int = 100


class Party(msgspec.Struct):
    """A group of adventurers finding themselves doing and saying things altogether unexpected.

    Attributes:
        name (str): Name that party is known by
        formed_datetime (datetime): Timestamp of when the party was formed
        members (list[Adventurer]): Adventurers that belong to this party
        active_quest (Optional[Quest]): Current quest that party is actively tackling
    """

    name: str
    formed_datetime: datetime
    members: list[Adventurer] = []
    active_quest: Optional[Quest] = None
