import builtins
import dataclasses
import sys
from typing import List, Optional

import IPython.lib.pretty as IPython_pretty
import pytest
import rich

from erdantic.core import (
    EntityRelationshipDiagram,
    FieldInfo,
    FullyQualifiedName,
    ModelInfo,
    SortedDict,
)
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


@pytest.fixture
def no_rich(monkeypatch):
    """Remove rich from imported modules, and patch import to pretend it's not installed."""
    # Remove if already imported
    rich_module = sys.modules.pop("rich", None)
    # Patch import
    import_orig = builtins.__import__

    def mocked_import(name, globals, locals, fromlist, level):
        if name == "rich":
            raise ModuleNotFoundError(name=name, path=__file__)
        return import_orig(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", mocked_import)

    yield

    if rich_module:
        sys.modules["rich"] = rich_module


def test_ipython_repr_pretty_no_rich(no_rich):
    """IPython _repr_pretty_ methods should run without error when rich isn't installed."""
    # Rich should not be available or importable because of our fixture
    assert "rich" not in sys.modules
    with pytest.raises(ModuleNotFoundError):
        import rich  # noqa: F401

    diagram = EntityRelationshipDiagram()
    diagram.add_model(Party)

    IPython_pretty.pprint(diagram)
    IPython_pretty.pprint(diagram.models)  # SortedDict of ModelInfo instances
    model_info = next(iter(diagram.models.values()))
    IPython_pretty.pprint(model_info)  # ModelInfo instance
    field_info = next(iter(model_info.fields.values()))
    IPython_pretty.pprint(field_info)  # FieldInfo instance
    IPython_pretty.pprint(diagram.edges)  # SortedDict of Edge instances
    edge = next(iter(diagram.edges.values()))
    IPython_pretty.pprint(edge)  # Edge instance

    sorted_dict = SortedDict({"a": 1, "b": 2})
    IPython_pretty.pprint(sorted_dict)


@pytest.fixture
def mock_rich_print(monkeypatch):
    """Mock rich.print to check if it was called."""

    class MockedRichPrint:
        def __init__(self):
            self.called = False

        def __call__(self, *args, **kwargs):
            self.called = True

        def was_called(self):
            if self.called:
                self.called = False
                return True
            return False

    mocked_rich_print = MockedRichPrint()
    monkeypatch.setattr(rich, "print", mocked_rich_print)
    yield mocked_rich_print


def test_ipython_repr_pretty_with_rich(mock_rich_print):
    """IPython _repr_pretty_ methods should run and call rich if installed."""
    diagram = EntityRelationshipDiagram()
    diagram.add_model(Party)

    assert not mock_rich_print.was_called()

    IPython_pretty.pprint(diagram)
    assert mock_rich_print.was_called()
    assert not mock_rich_print.was_called()

    IPython_pretty.pprint(diagram.models)  # SortedDict of ModelInfo instances
    assert mock_rich_print.was_called()
    assert not mock_rich_print.was_called()

    model_info = next(iter(diagram.models.values()))
    IPython_pretty.pprint(model_info)  # ModelInfo instance
    assert mock_rich_print.was_called()
    assert not mock_rich_print.was_called()

    field_info = next(iter(model_info.fields.values()))
    IPython_pretty.pprint(field_info)  # FieldInfo instance
    assert mock_rich_print.was_called()
    assert not mock_rich_print.was_called()

    IPython_pretty.pprint(diagram.edges)  # SortedDict of Edge instances
    assert mock_rich_print.was_called()
    assert not mock_rich_print.was_called()

    edge = next(iter(diagram.edges.values()))
    IPython_pretty.pprint(edge)  # Edge instance
    assert mock_rich_print.was_called()
    assert not mock_rich_print.was_called()

    sorted_dict = SortedDict({"a": 1, "b": 2})
    IPython_pretty.pprint(sorted_dict)
    assert mock_rich_print.was_called()
    assert not mock_rich_print.was_called()


def test_rich_print():
    """rich.print should work on EntityRelationshipDiagram and SortedDict without error."""
    diagram = EntityRelationshipDiagram()
    diagram.add_model(Party)
    rich.print(diagram)

    sorted_dict = SortedDict({"a": 1, "b": 2})
    rich.print(sorted_dict)
