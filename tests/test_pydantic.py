from erdantic.core import FullyQualifiedName
import erdantic.examples.pydantic as pydantic_examples
import erdantic.examples.pydantic_v1 as pydantic_v1_examples
from erdantic.plugins.pydantic import (
    get_fields_from_pydantic_model,
    get_fields_from_pydantic_v1_model,
    is_pydantic_model,
    is_pydantic_v1_model,
)


def test_is_pydantic_model():
    class NotAPydanticModel:
        pass

    assert is_pydantic_model(pydantic_examples.Party)
    assert is_pydantic_model(pydantic_examples.QuestGiver)
    assert not is_pydantic_model(
        pydantic_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_pydantic_model("Hello")
    assert not is_pydantic_model(str)
    assert not is_pydantic_model(NotAPydanticModel)
    assert not is_pydantic_model(pydantic_v1_examples.Party)


def test_get_fields_from_pydantic_model():
    fields = get_fields_from_pydantic_model(pydantic_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(pydantic_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(pydantic_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(pydantic_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "List[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(pydantic_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"


def test_is_pydantic_v1_model():
    class NotAPydanticModel:
        pass

    assert is_pydantic_v1_model(pydantic_v1_examples.Party)
    assert is_pydantic_v1_model(pydantic_v1_examples.QuestGiver)
    assert not is_pydantic_v1_model(
        pydantic_v1_examples.QuestGiver(name="Gandalf", faction=None, location="Shire")
    )
    assert not is_pydantic_v1_model("Hello")
    assert not is_pydantic_v1_model(str)
    assert not is_pydantic_v1_model(NotAPydanticModel)
    assert not is_pydantic_v1_model(pydantic_examples.Party)


def test_get_fields_from_pydantic_v1_model():
    fields = get_fields_from_pydantic_v1_model(pydantic_v1_examples.Party)
    assert len(fields) == 4

    # name
    assert fields[0].model_full_name == FullyQualifiedName.from_object(pydantic_v1_examples.Party)
    assert fields[0].name == "name"
    assert fields[0].type_name == "str"
    # formed_datetime
    assert fields[1].model_full_name == FullyQualifiedName.from_object(pydantic_v1_examples.Party)
    assert fields[1].name == "formed_datetime"
    assert fields[1].type_name == "datetime"
    # members
    assert fields[2].model_full_name == FullyQualifiedName.from_object(pydantic_v1_examples.Party)
    assert fields[2].name == "members"
    assert fields[2].type_name == "List[Adventurer]"
    # active_quest
    assert fields[3].model_full_name == FullyQualifiedName.from_object(pydantic_v1_examples.Party)
    assert fields[3].name == "active_quest"
    assert fields[3].type_name == "Optional[Quest]"
