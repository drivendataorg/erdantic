from enum import Enum, IntFlag
import sys
import typing

from typing import ForwardRef  # docs claim Python >= 3.7.4 but actually it's in Python 3.7.0+

try:
    from typing import Literal  # type: ignore # Python >=3.8
except ImportError:
    try:
        from typing_extensions import Literal  # type: ignore # Python ==3.7.*
    except ImportError:
        Literal = None  # type: ignore # Python <3.7


import pytest

from erdantic.typing import (
    get_depth1_bases,
    get_recursive_args,
    repr_enum,
    repr_type,
    repr_type_with_mro,
)


def test_get_recursive_args():
    tp = typing.Optional[typing.Dict[str, typing.List[typing.Tuple[int, float]]]]
    args = get_recursive_args(tp)
    assert isinstance(args, list)
    assert set(args) == {str, int, float, type(None)}

    assert get_recursive_args(str) == [str]
    if Literal is not None:
        assert get_recursive_args(Literal["batman"]) in [[Literal], [Literal["batman"]]]


def test_get_depth1_bases():
    class A0:
        pass

    class A1(A0):
        pass

    class A2(A1):
        pass

    class B0:
        pass

    class B1(B0):
        pass

    class C:
        pass

    class SubClass(str, A2, B1, C):
        pass

    get_depth1_bases(SubClass) == [str, A2, B1, C]


class MyEnum(Enum):
    FOO = "bar"


class MyStrEnum(str, Enum):
    FOO = "bar"


class MyIntFlag(IntFlag):
    FOO = 0


def test_repr_enum():
    assert repr_enum(MyEnum) == "MyEnum(Enum)"
    assert repr_enum(MyStrEnum) == "MyStrEnum(str, Enum)"
    assert repr_enum(MyIntFlag) == "MyIntFlag(IntFlag)"


class MyClass:
    pass


repr_type_cases = [
    (int, "int"),
    (typing.List[int], "List[int]"),
    (typing.Tuple[str, int], "Tuple[str, int]"),
    (typing.Optional[int], "Optional[int]"),
    (MyClass, "MyClass"),
    (typing.List[MyClass], "List[MyClass]"),
    (typing.Optional[typing.List[MyClass]], "Optional[List[MyClass]]"),
    (typing.Union[float, int], "Union[float, int]"),
    (typing.Dict[str, int], "Dict[str, int]"),
    (typing.Optional[MyStrEnum], "Optional[MyStrEnum(str, Enum)]"),
    (typing.List[MyIntFlag], "List[MyIntFlag(IntFlag)]"),
    (typing.Any, "Any"),
    (typing.Dict[str, typing.Any], "Dict[str, Any]"),
    (ForwardRef("MyClass"), "MyClass"),
]

if sys.version_info[:2] >= (3, 9):
    # Python 3.9 adds [] support to builtin generics
    repr_type_cases.extend(
        [
            (list[int], "list[int]"),
            (dict[str, list[int]], "dict[str, list[int]]"),
        ]
    )


@pytest.mark.parametrize("case", repr_type_cases, ids=[c[1] for c in repr_type_cases])
def test_repr_type(case):
    tp, expected = case
    assert repr_type(tp) == expected


def test_repr_type_literal():
    tp = Literal["batman"]
    assert "Literal['batman']" in repr_type(tp)


def test_repr_type_with_mro():
    class FancyInt(int):
        pass

    assert (
        repr_type_with_mro(FancyInt)
        == "<mro (tests.test_typing.test_repr_type_with_mro.<locals>.FancyInt, int, object)>"
    )
    assert repr_type_with_mro(FancyInt()) == repr(FancyInt())
