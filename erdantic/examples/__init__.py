"""Example data model classes."""

import sys

from erdantic.examples import dataclasses, msgspec, pydantic

if sys.version_info < (3, 14):
    from erdantic.examples import pydantic_v1

__all__ = [
    "dataclasses",
    "msgspec",
    "pydantic",
    "pydantic_v1",
]

try:
    from erdantic.examples import attrs

    attrs
    __all__.append("attrs")
except ModuleNotFoundError as e:
    if e.name != "attrs":
        raise
