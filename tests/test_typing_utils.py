import typing

import pytest

from erdantic.exceptions import _UnevaluatedForwardRefError
from erdantic.typing_utils import (
    get_depth1_bases,
    get_recursive_args,
    is_collection_type_of,
    is_nullable_type,
    repr_type_with_mro,
)


def test_is_collection_type_of():
    class Target: ...

    assert is_collection_type_of(typing.List[Target], Target)
    assert is_collection_type_of(typing.Optional[typing.List[Target]], Target)
    assert is_collection_type_of(typing.List[typing.Optional[Target]], Target)
    assert is_collection_type_of(typing.Union[Target, typing.List[Target], None], Target)

    assert not is_collection_type_of(Target, Target)
    assert not is_collection_type_of(typing.Optional[Target], Target)
    assert not is_collection_type_of(typing.Union[Target, int], Target)
    assert not is_collection_type_of(typing.List[int], Target)
    assert not is_collection_type_of(typing.Union[Target, typing.List[int]], Target)


def test_is_nullable_type():
    assert is_nullable_type(typing.Optional[int])
    assert is_nullable_type(typing.Union[int, None])
    assert is_nullable_type(typing.Union[int, str, None])

    assert not is_nullable_type(int)
    assert not is_nullable_type(typing.Union[int, str])


def test_get_recursive_args():
    tp = typing.Optional[typing.Dict[str, typing.List[typing.Tuple[int, float]]]]
    args = get_recursive_args(tp)
    assert isinstance(args, list)
    assert set(args) == {str, int, float, type(None)}

    assert get_recursive_args(str) == [str]
    assert get_recursive_args(typing.Union[int, typing.Literal["batman"]]) == [
        int,
        typing.Literal["batman"],
    ]

    T = typing.TypeVar("T")
    assert get_recursive_args(typing.Union[int, typing.List[T]]) == [int, T]

    class SomeForwardRef: ...

    with pytest.raises(_UnevaluatedForwardRefError):
        get_recursive_args("SomeForwardRef")

    with pytest.raises(_UnevaluatedForwardRefError):
        get_recursive_args(typing.List["SomeForwardRef"])

    # Test typing.ForwardRef case
    class Model:
        field: typing.List["SomeForwardRef"]

    # Forward reference is not resolved yet
    with pytest.raises(_UnevaluatedForwardRefError):
        get_recursive_args(Model.__annotations__["field"])

    # Resolve forward reference
    typing.get_type_hints(Model, localns=locals())

    assert get_recursive_args(Model.__annotations__["field"]) == [SomeForwardRef]


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


def test_repr_type_with_mro():
    class FancyInt(int):
        pass

    assert (
        repr_type_with_mro(FancyInt)
        == "<mro (tests.test_typing_utils.test_repr_type_with_mro.<locals>.FancyInt, int, object)>"
    )
    assert repr_type_with_mro(FancyInt()) == repr(FancyInt())
