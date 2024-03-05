from erdantic.core import FullyQualifiedName
import erdantic.examples.dataclasses as dataclasses_examples
from erdantic.plugins.dataclasses import (
    get_fields_from_dataclass,
    is_dataclass_type,
)


def test_is_pydantic_model():
    class NotAPydanticModel:
        pass

    assert is_dataclass_type(dataclasses_examples.Party)
    assert is_dataclass_type(dataclasses_examples.QuestGiver)
    assert not is_dataclass_type(
        dataclasses_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_dataclass_type("Hello")
    assert not is_dataclass_type(str)
    assert not is_dataclass_type(NotAPydanticModel)


def test_get_fields_from_dataclass():
    fields = get_fields_from_dataclass(dataclasses_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(dataclasses_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(dataclasses_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(dataclasses_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "List[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(dataclasses_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"
