import dataclasses
from typing import List

import pytest

from erdantic.core import EntityRelationshipDiagram, FieldInfo, FullyQualifiedName
from erdantic.examples.dataclasses import Party
import erdantic.plugins._registry
from erdantic.plugins.dataclasses import DataclassType


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
    dataclasses_predicate_fn = erdantic.plugins._registry.get_predicate_fn("dataclasses")
    patch = (
        dataclasses_predicate_fn,
        get_fields_from_dataclass_no_get_type_hints,
    )
    monkeypatch.setitem(erdantic.plugins._registry._dict, "dataclasses", patch)

    @dataclasses.dataclass
    class Game:
        party: "Party"

    diagram = EntityRelationshipDiagram()
    with pytest.raises(erdantic.exceptions.UnevaluatedForwardRefError):
        diagram.add_model(Game)
