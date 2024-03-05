from erdantic.core import FullyQualifiedName
import erdantic.examples.attrs as attrs_examples
from erdantic.plugins.attrs import (
    get_fields_from_attrs_class,
    is_attrs_class,
)


def test_is_pydantic_model():
    class NotAPydanticModel:
        pass

    assert is_attrs_class(attrs_examples.Party)
    assert is_attrs_class(attrs_examples.QuestGiver)
    assert not is_attrs_class(
        attrs_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_attrs_class("Hello")
    assert not is_attrs_class(str)
    assert not is_attrs_class(NotAPydanticModel)


def test_get_fields_from_attrs_class():
    fields = get_fields_from_attrs_class(attrs_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(attrs_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(attrs_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(attrs_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "List[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(attrs_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"
