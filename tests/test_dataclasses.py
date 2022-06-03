import dataclasses
from typing import Dict, List, Tuple, get_type_hints

from typing import ForwardRef  # docs claim Python >= 3.7.4 but actually it's in Python 3.7.0+

import pytest

import erdantic as erd
from erdantic.exceptions import StringForwardRefError, UnevaluatedForwardRefError


def test_model_graph_search_nested_args():
    @dataclasses.dataclass
    class Inner0:
        id: int

    @dataclasses.dataclass
    class Inner1:
        id: int

    @dataclasses.dataclass
    class Outer:
        inner: Dict[str, Tuple[Inner0, Inner1]]

    diagram = erd.create(Outer)
    assert {m.model for m in diagram.models} == {Outer, Inner0, Inner1}
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {
        (Outer, Inner0),
        (Outer, Inner1),
    }


def test_string_forward_ref():
    @dataclasses.dataclass
    class WithStringForwardRef:
        sibling: "WithStringForwardRef"

    get_type_hints(WithStringForwardRef, localns=locals())

    # Unevaluated forward ref should error
    with pytest.raises(StringForwardRefError):
        _ = erd.create(WithStringForwardRef)

    @dataclasses.dataclass
    class WithExplicitForwardRef:
        sibling: ForwardRef("WithExplicitForwardRef")  # noqa: F821

    get_type_hints(WithExplicitForwardRef, localns=locals())

    diagram = erd.create(WithExplicitForwardRef)
    assert {m.model for m in diagram.models} == {WithExplicitForwardRef}
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {
        (WithExplicitForwardRef, WithExplicitForwardRef)
    }


def test_unevaluated_forward_ref():
    @dataclasses.dataclass
    class DataClassItem:
        name: str

    @dataclasses.dataclass
    class DataClassContainer:
        items: List["DataClassItem"]

    # Unevaluated forward ref should error
    with pytest.raises(UnevaluatedForwardRefError, match="get_type_hints"):
        _ = erd.create(DataClassContainer)

    # Evaluate forward ref
    get_type_hints(DataClassContainer, localns=locals())

    # Test that class can be initialized
    _ = DataClassContainer(items=[DataClassItem(name="thingie")])

    diagram = erd.create(DataClassContainer)
    assert {m.model for m in diagram.models} == {DataClassContainer, DataClassItem}
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {
        (DataClassContainer, DataClassItem)
    }
