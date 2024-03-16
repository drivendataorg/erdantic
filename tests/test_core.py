import dataclasses
from typing import List, Optional

import pytest

from erdantic.core import EntityRelationshipDiagram, FieldInfo, FullyQualifiedName, ModelInfo
from erdantic.examples.dataclasses import Adventurer, Party
from erdantic.exceptions import FieldNotFoundError, UnknownModelTypeError
import erdantic.plugins
from erdantic.plugins.dataclasses import DataclassType


def test_fully_qualified_name_import_object():
    full_name = FullyQualifiedName.from_object(Party)
    assert full_name.import_object() == Party


def test_field_info_raw_type():
    """FieldInfo can recover the raw type from its information."""
    field_info = FieldInfo(
        model_full_name=FullyQualifiedName.from_object(Party),
        name="members",
        type_name="this_is_arbitrary",
    )
    assert field_info.raw_type == List[Adventurer]


def test_field_not_found_error():
    """A FieldInfo for a model field that does not exist should error if trying to get the raw
    type."""

    field_info = FieldInfo(
        model_full_name=FullyQualifiedName.from_object(Party),
        name="not_a_field",
        type_name="str",
    )
    with pytest.raises(FieldNotFoundError) as exc_info:
        field_info.raw_type
    assert exc_info.match(f"'{FullyQualifiedName.from_object(Party)}'")
    assert exc_info.match("'not_a_field'")


def test_model_info_raw_model():
    """A ModelInfo instance can recover the raw model from its information."""
    model_info = ModelInfo(
        full_name=FullyQualifiedName.from_object(Party), name="this_is_arbitrary", fields={}
    )
    assert model_info.raw_model == Party


def test_add_unknown_model_type():
    class NotAModel: ...

    diagram = EntityRelationshipDiagram()
    with pytest.raises(UnknownModelTypeError):
        diagram.add_model(NotAModel)


def test_unsupported_forward_ref_resolution(monkeypatch):
    """Plugin implementation does not do anything to resolve forward references."""

    def get_fields_from_dataclass_no_get_type_hints(model: DataclassType) -> List[FieldInfo]:
        """Version of get_fields_from_dataclass that doesn't use get_type_hints and doesn't do
        anything to resolve forward references."""
        return [
            FieldInfo.from_raw_type(
                model_full_name=FullyQualifiedName.from_object(model),
                name=f.name,
                raw_type=f.type,
            )
            for f in dataclasses.fields(model)
        ]

    # Patch dataclasses plugin
    dataclasses_predicate_fn = erdantic.plugins.get_predicate_fn("dataclasses")
    patch = (
        dataclasses_predicate_fn,
        get_fields_from_dataclass_no_get_type_hints,
    )
    monkeypatch.setitem(erdantic.plugins._dict, "dataclasses", patch)

    # Test bare string forward reference
    @dataclasses.dataclass
    class Game:
        party: "Party"

    diagram = EntityRelationshipDiagram()
    with pytest.raises(erdantic.exceptions.UnevaluatedForwardRefError):
        diagram.add_model(Game)

    # Test nested forward reference
    @dataclasses.dataclass
    class Game:
        party: Optional["Party"]

    diagram = EntityRelationshipDiagram()
    with pytest.raises(erdantic.exceptions.UnevaluatedForwardRefError):
        diagram.add_model(Game)
