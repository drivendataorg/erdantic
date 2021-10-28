import dataclasses
from typing import Dict, List, Tuple, get_type_hints

import pytest

import erdantic as erd
from erdantic.exceptions import UnevaluatedForwardRefError


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


def test_forward_references():
    @dataclasses.dataclass
    class Item:
        name: str

    @dataclasses.dataclass
    class Container:
        items: List["Item"]

    # Unevaluated forward ref should error
    with pytest.raises(UnevaluatedForwardRefError, match="get_type_hints"):
        _ = erd.create(Container)

    # Evaluate forward ref
    get_type_hints(Container, localns=locals())

    # Test that class can be initialized
    _ = Container(items=[Item(name="thingie")])

    diagram = erd.create(Container)
    assert {m.model for m in diagram.models} == {Container, Item}
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {(Container, Item)}
