import pytest

from erdantic.convenience import create, find_models
from erdantic.core import EntityRelationshipDiagram, FullyQualifiedName
import erdantic.examples.dataclasses as dataclasses_examples
import erdantic.examples.pydantic as pydantic_examples
from erdantic.exceptions import PluginNotFoundError


def test_find_models():
    expected_pydantic_models = {
        pydantic_examples.Party,
        pydantic_examples.Adventurer,
        pydantic_examples.Quest,
        pydantic_examples.QuestGiver,
    }
    assert set(find_models(pydantic_examples)) == expected_pydantic_models
    assert (
        set(find_models(pydantic_examples, limit_search_models_to=["pydantic"]))
        == expected_pydantic_models
    )
    assert set(find_models(pydantic_examples, limit_search_models_to=["dataclasses"])) == set()

    expected_dataclasses_models = {
        dataclasses_examples.Party,
        dataclasses_examples.Adventurer,
        dataclasses_examples.Quest,
        dataclasses_examples.QuestGiver,
    }
    assert set(find_models(dataclasses_examples)) == expected_dataclasses_models

    with pytest.raises(PluginNotFoundError):
        list(find_models(pydantic_examples, limit_search_models_to=["unknown_key"]))


def test_create():
    expected = EntityRelationshipDiagram()
    expected.add_model(pydantic_examples.Party)

    # With model
    assert create(pydantic_examples.Party) == expected
    # With module
    assert create(pydantic_examples) == expected


def test_terminal_models():
    # Test terminal_models
    diagram = create(pydantic_examples.Party, terminal_models=[pydantic_examples.Quest])
    expected_model_keys = sorted(
        str(FullyQualifiedName.from_object(model))
        for model in [
            pydantic_examples.Party,
            pydantic_examples.Adventurer,
            pydantic_examples.Quest,
        ]
    )
    assert list(diagram.models.keys()) == expected_model_keys


def test_termini():
    # Test termini, should work but throw a deprecation warning
    with pytest.deprecated_call():
        diagram = create(pydantic_examples.Party, termini=[pydantic_examples.Quest])
    expected_model_keys = sorted(
        str(FullyQualifiedName.from_object(model))
        for model in [
            pydantic_examples.Party,
            pydantic_examples.Adventurer,
            pydantic_examples.Quest,
        ]
    )
    assert list(diagram.models.keys()) == expected_model_keys

    # Using both termini and terminal_models should raise a ValueError
    with pytest.raises(ValueError), pytest.deprecated_call():
        create(
            pydantic_examples.Party,
            terminal_models=[pydantic_examples.Quest],
            termini=[pydantic_examples.Adventurer],
        )
