import builtins
import dataclasses
import filecmp
import os
from pathlib import Path
import sys
from typing import Any, AnyStr, List, Literal, Optional, Tuple, TypeVar

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

import IPython.lib.pretty as IPython_pretty
import pydantic
import pytest
import rich

from erdantic.core import (
    Edge,
    EntityRelationshipDiagram,
    FieldInfo,
    FullyQualifiedName,
    ModelInfo,
    SortedDict,
)
import erdantic.examples.dataclasses as dataclasses_examples
from erdantic.examples.dataclasses import Adventurer, Party
import erdantic.examples.pydantic as pydantic_examples
from erdantic.exceptions import FieldNotFoundError, UnknownModelTypeError
import erdantic.plugins
from erdantic.plugins.dataclasses import DataclassType

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def test_fully_qualified_name_import_object():
    full_name = FullyQualifiedName.from_object(Party)
    assert full_name.import_object() == Party


def test_fully_qualified_name_sorting():
    full_name1 = FullyQualifiedName.from_object(Adventurer)
    full_name2 = FullyQualifiedName.from_object(Party)
    assert full_name1 < full_name2
    assert full_name1 <= full_name2
    assert full_name1 <= full_name1
    assert full_name2 > full_name1
    assert full_name2 >= full_name1
    assert full_name2 >= full_name2
    assert full_name1 != full_name2
    assert full_name1 == full_name1
    assert full_name2 == full_name2
    sorted([full_name1, full_name2]) == [full_name1, full_name2]
    sorted([full_name2, full_name1]) == [full_name1, full_name2]


def test_fully_qualified_name_hash():
    full_name1 = FullyQualifiedName.from_object(Adventurer)
    full_name2 = FullyQualifiedName.from_object(Adventurer)
    full_name3 = FullyQualifiedName.from_object(Party)

    assert hash(full_name1) == hash(full_name2)
    assert hash(full_name1) != hash(full_name3)
    assert hash(full_name2) != hash(full_name3)


def test_field_info_raw_type():
    """FieldInfo can recover the raw type from its information."""
    field_info = FieldInfo(
        model_full_name=FullyQualifiedName.from_object(Party),
        name="members",
        type_name="this_is_arbitrary",
    )
    assert field_info.raw_type == List[Adventurer]


def test_field_info_annotated():
    """FieldInfo should handle Annotated types. The type_name should not included metadata."""

    class DummyModel: ...

    tp = Annotated[str, "metadata"]
    field_info = FieldInfo.from_raw_type(
        model_full_name=FullyQualifiedName.from_object(DummyModel), name="dummy", raw_type=tp
    )
    assert field_info.type_name == "str"
    assert field_info.raw_type == tp

    tp = Annotated[str, object()]
    field_info = FieldInfo.from_raw_type(
        model_full_name=FullyQualifiedName.from_object(DummyModel), name="dummy", raw_type=tp
    )
    assert field_info.type_name == "str"
    assert field_info.raw_type == tp

    tp = Optional[Annotated[str, object()]]
    field_info = FieldInfo.from_raw_type(
        model_full_name=FullyQualifiedName.from_object(DummyModel), name="dummy", raw_type=tp
    )
    assert field_info.type_name == "Optional[str]"
    assert field_info.raw_type == tp


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


def test_equality():
    """Test equality methods on EntityRelationshipDiagram, ModelInfo, FieldInfo, and Edge."""

    diagram1 = EntityRelationshipDiagram()
    diagram1.add_model(dataclasses_examples.Party)

    diagram2 = EntityRelationshipDiagram()
    diagram2.add_model(dataclasses_examples.Party)

    diagram3 = EntityRelationshipDiagram()
    diagram3.add_model(pydantic_examples.Party)
    different_model = next(iter(diagram3.models.values()))
    different_field = next(iter(different_model.fields.values()))
    different_edge = next(iter(diagram3.edges.values()))

    assert diagram1 == diagram2
    assert diagram1 != diagram3
    assert diagram2 != diagram3
    assert list(diagram1.models.keys()) == list(diagram2.models.keys())
    for model_key in diagram1.models.keys():
        model1 = diagram1.models[model_key]
        model2 = diagram2.models[model_key]
        assert model1 == model2
        assert model1 != different_model
        assert model2 != different_model
        assert list(model1.fields.keys()) == list(model2.fields.keys())
        for field_key in model1.fields.keys():
            field1 = model1.fields[field_key]
            field2 = model2.fields[field_key]
            assert field1 == field2
            assert field1 != different_field
            assert field2 != different_field
    assert list(diagram1.edges.keys()) == list(diagram2.edges.keys())
    for edge_key in diagram1.edges.keys():
        edge1 = diagram1.edges[edge_key]
        edge2 = diagram2.edges[edge_key]
        assert edge1 == edge2
        assert edge1 != different_edge
        assert edge2 != different_edge


def test_key():
    """key method on ModelInfo, FieldInfo, and Edge should match key of dictionaries."""
    diagram = EntityRelationshipDiagram()
    diagram.add_model(Party)

    for model_key, model_info in diagram.models.items():
        assert model_info.key == model_key
        for field_key, field_info in model_info.fields.items():
            assert field_info.key == field_key
    for edge_key, edge in diagram.edges.items():
        assert edge.key == edge_key


def test_add_unknown_model_type():
    class NotAModel: ...

    diagram = EntityRelationshipDiagram()
    with pytest.raises(UnknownModelTypeError):
        diagram.add_model(NotAModel)


def test_model_with_typing_special_forms():
    """Models may have special forms in the leaf nodes and we should handle it."""

    T = TypeVar("T")

    class MyModel(pydantic.BaseModel):
        any_field: Any
        literal_field: Literal["a", "b", "c"]
        type_var_field: T
        anystr_field: AnyStr

    diagram = EntityRelationshipDiagram()
    diagram.add_model(MyModel)
    diagram.to_dot()


def test_model_with_ellipsis():
    """Model with Ellipsis should not error."""

    class EllipsisModel(pydantic.BaseModel):
        ellipsis_field: Tuple[int, ...]

    diagram = EntityRelationshipDiagram()
    diagram.add_model(EllipsisModel)
    diagram.to_dot()


def test_model_with_no_fields():
    """Model with no fields should not error."""

    class EmptyModel(pydantic.BaseModel):
        pass

    diagram = EntityRelationshipDiagram()
    diagram.add_model(EmptyModel)
    diagram.to_dot()


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


def test_ipython_repr_png():
    """IPython _repr_png_ method should run without error."""
    diagram = EntityRelationshipDiagram()
    diagram.add_model(Party)
    assert diagram._repr_png_()


def test_ipython_repr_svg():
    """IPython _repr_svg_ method should run without error."""
    diagram = EntityRelationshipDiagram()
    diagram.add_model(Party)
    assert diagram._repr_svg_()


def test_model_info_subclass():
    class CustomModelInfo(ModelInfo):
        pass

    class CustomEntityRelationshipDiagram(EntityRelationshipDiagram):
        models: SortedDict[str, CustomModelInfo] = SortedDict()

    diagram = CustomEntityRelationshipDiagram()
    diagram.add_model(Party)
    assert all(isinstance(model_info, CustomModelInfo) for model_info in diagram.models.values())


def test_edge_subclass():
    class CustomEdge(Edge):
        pass

    class CustomEntityRelationshipDiagram(EntityRelationshipDiagram):
        edges: SortedDict[str, CustomEdge] = SortedDict()

    diagram = CustomEntityRelationshipDiagram()
    diagram.add_model(Party)
    assert all(isinstance(edge, CustomEdge) for edge in diagram.edges.values())


@pytest.fixture
def reset_plugins():
    """Reset plugins to original state after we test overwriting pydantic plugin."""
    plugins_data = tuple(erdantic.plugins._dict.items())
    yield
    erdantic.plugins._dict = dict(plugins_data)


def test_subclass(caplog, outputs_dir, version_patch, reset_plugins):
    """Subclass things to add a third column with the field default value."""
    out_dir = outputs_dir / "test_score-test_subclass"
    out_dir.mkdir()
    filename = "pydantic_with_default_column"

    # Import module that implements custom classes
    import tests.pydantic_with_default_column

    # Should log warning that we're overwriting pydantic plugin
    warning_records = [record for record in caplog.records if record.levelname == "WARNING"]
    assert len(warning_records) == 1
    assert "pydantic" in warning_records[0].message

    diagram = tests.pydantic_with_default_column.EntityRelationshipDiagramWithDefault()
    diagram.add_model(pydantic_examples.Party)

    expected_dir = ASSETS_DIR / "test_core-test_subclass"

    diagram.draw(out_dir / f"{filename}.png")
    if not os.getenv("GITHUB_ACTIONS", False):
        # Skip for CI because it doesn't produce an identical file
        assert filecmp.cmp(out_dir / f"{filename}.png", expected_dir / f"{filename}.png")

    diagram.draw(out_dir / f"{filename}.svg")
    if not os.getenv("GITHUB_ACTIONS", False):
        # Skip for CI because it doesn't produce an identical file
        assert (out_dir / f"{filename}.svg").read_text() == (
            expected_dir / f"{filename}.svg"
        ).read_text()

    (out_dir / f"{filename}.dot").write_text(diagram.to_dot())
    assert (out_dir / f"{filename}.dot").read_text() == (
        expected_dir / f"{filename}.dot"
    ).read_text()

    (out_dir / f"{filename}.json").write_text(diagram.model_dump_json(indent=2))
    assert (out_dir / f"{filename}.json").read_text() == (
        expected_dir / f"{filename}.json"
    ).read_text()
