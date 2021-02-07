import sys
import typing

import pytest

from erdantic.typing import get_args, get_origin


if sys.version_info[:2] >= (3, 7):

    class MyClass:
        pass

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
        assert get_args(tp) == typing.get_args(tp)

    @pytest.mark.parametrize("tp", test_cases)
    def test_get_origin(tp):
        assert get_origin(tp) == typing.get_origin(tp)
