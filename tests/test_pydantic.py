from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel

import erdantic as erd
from erdantic.pydantic import PydanticModel


def test_model_graph_search_nested_args():
    class Inner0(BaseModel):
        id: int

    class Inner1(BaseModel):
        id: int

    class Outer(BaseModel):
        inner: Dict[str, Tuple[Inner0, Inner1]]

    diagram = erd.create(Outer)
    assert {m.model for m in diagram.models} == {Outer, Inner0, Inner1}
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {
        (Outer, Inner0),
        (Outer, Inner1),
    }


def test_field_names():
    class MyClass(BaseModel):
        a: str
        b: Optional[str]
        c: List[str]
        d: Tuple[str, ...]
        e: Tuple[str, int]
        f: Dict[str, List[int]]
        g: Optional[List[str]]
        h: Dict[str, Optional[int]]

    model = PydanticModel(MyClass)
    assert [f.type_name for f in model.fields] == [
        "str",
        "Optional[str]",
        "List[str]",
        "Tuple[str, ...]",
        "Tuple[str, int]",
        "Dict[str, List[int]]",
        "Optional[List[str]]",
        "Dict[str, Optional[int]]",
    ]
