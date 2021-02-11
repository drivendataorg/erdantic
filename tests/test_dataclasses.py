import dataclasses
from typing import Dict, Tuple

import erdantic as erd


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
