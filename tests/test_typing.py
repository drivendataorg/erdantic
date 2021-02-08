from enum import Enum, IntFlag
import sys
import typing

import pytest

from erdantic.typing import _get_args, _get_origin, repr_enum, repr_type, get_depth1_bases


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
]

if sys.version_info[:2] >= (3, 9):
    # Python 3.9 adds [] support to builtin generics
    repr_type_cases.extend(
        [
            (list[int], "list[int]"),
            (dict[str, list[int]], "dict[str, list[int]]"),
        ]
    )


@pytest.mark.parametrize("case", repr_type_cases)
def test_repr_type(case):
    tp, expected = case
    assert repr_type(tp) == expected


# Test backports
if sys.version_info[:2] >= (3, 7):

    test_cases = [
        int,
        typing.List[int],
        typing.Optional[int],
        MyClass,
        typing.List[MyClass],
        typing.Optional[MyClass],
    ]

    @pytest.mark.parametrize("tp", test_cases)
    def test_get_args(tp):
        assert _get_args(tp) == typing.get_args(tp)

    @pytest.mark.parametrize("tp", test_cases)
    def test_get_origin(tp):
        assert _get_origin(tp) == typing.get_origin(tp)
