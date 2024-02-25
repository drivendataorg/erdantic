import typing
from typing import Literal

from erdantic.typing import (
    get_depth1_bases,
    get_recursive_args,
    is_many,
    is_nullable,
    repr_type_with_mro,
)


def test_is_many():
    class Target:
        ...

    assert is_many(typing.List[Target], Target)
    assert is_many(typing.Optional[typing.List[Target]], Target)
    assert is_many(typing.List[typing.Optional[Target]], Target)
    assert is_many(typing.Union[Target, typing.List[Target], None], Target)

    assert not is_many(Target, Target)
    assert not is_many(typing.Optional[Target], Target)
    assert not is_many(typing.Union[Target, int], Target)
    assert not is_many(typing.List[int], Target)
    assert not is_many(typing.Union[Target, typing.List[int]], Target)


def test_is_nullable():
    assert is_nullable(typing.Optional[int])
    assert is_nullable(typing.Union[int, None])
    assert is_nullable(typing.Union[int, str, None])

    assert not is_nullable(int)
    assert not is_nullable(typing.Union[int, str])


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


def test_repr_type_with_mro():
    class FancyInt(int):
        pass

    assert (
        repr_type_with_mro(FancyInt)
        == "<mro (tests.test_typing.test_repr_type_with_mro.<locals>.FancyInt, int, object)>"
    )
    assert repr_type_with_mro(FancyInt()) == repr(FancyInt())
