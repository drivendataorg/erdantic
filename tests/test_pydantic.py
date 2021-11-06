import textwrap
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
import pytest

import erdantic as erd
from erdantic.exceptions import UnevaluatedForwardRefError
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


def test_unevaluated_forward_ref():
    class PydanticItem(BaseModel):
        name: str

    class PydanticContainer(BaseModel):
        items: List["PydanticItem"]

    # Unevaluated forward ref should error
    with pytest.raises(UnevaluatedForwardRefError, match="update_forward_refs"):
        _ = erd.create(PydanticContainer)

    # Evaluate forward ref
    PydanticContainer.update_forward_refs(**locals())

    # Test that model can be used
    _ = PydanticContainer(items=[PydanticItem(name="thingie")])

    diagram = erd.create(PydanticContainer)
    assert {m.model for m in diagram.models} == {PydanticContainer, PydanticItem}
    assert {(e.source.model, e.target.model) for e in diagram.edges} == {
        (PydanticContainer, PydanticItem)
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


def test_docstring_field_descriptions():
    # Does not use pydantic.Field with descriptions. Shouldn't add anything.
    class MyClassWithoutDescriptions(BaseModel):
        """This is the docstring for my class without descriptions."""

        hint_only: str
        no_descr_has_default: Any = Field(10)

    model = PydanticModel(MyClassWithoutDescriptions)
    print("===Actual w/o Descriptions===")
    print(model.docstring)
    print("============")

    expected = textwrap.dedent(
        """\
        tests.test_pydantic.test_docstring_field_descriptions.<locals>.MyClassWithoutDescriptions

        This is the docstring for my class without descriptions.
        """
    )
    assert model.docstring == expected

    # Does use pydantic.Field with descriptions. Should add attributes section

    class MyClassWithDescriptions(BaseModel):
        """This is the docstring for my class with descriptions."""

        hint_only: str
        has_descr_no_default: List[int] = Field(description="An array of numbers.")
        has_descr_ellipsis_default: List[int] = Field(..., description="Another array of numbers.")
        no_descr_has_default: Any = Field(10)
        has_descr_has_default: Optional[str] = Field(None, description="An optional string.")

    model = PydanticModel(MyClassWithDescriptions)
    print("===Actual w/ Descriptions===")
    print(model.docstring)
    print("============")

    expected = textwrap.dedent(
        """\
        tests.test_pydantic.test_docstring_field_descriptions.<locals>.MyClassWithDescriptions

        This is the docstring for my class with descriptions.

        Attributes:
            has_descr_no_default (List[int]): An array of numbers.
            has_descr_ellipsis_default (List[int]): Another array of numbers.
            has_descr_has_default (Optional[str]): An optional string. Default is None.
        """
    )
    assert model.docstring == expected
