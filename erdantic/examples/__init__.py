"""Example data model classes."""

import sys

from erdantic.examples import dataclasses, pydantic

__all__ = [
    "dataclasses",
    "pydantic",
]

if sys.version_info < (3, 14):
    from erdantic.examples import pydantic_v1

    pydantic_v1
    __all__.append("pydantic_v1")

try:
    from erdantic.examples import attrs

    attrs
    __all__.append("attrs")
except ModuleNotFoundError as e:
    if e.name != "attrs":
        raise

try:
    from erdantic.examples import msgspec

    msgspec
    __all__.append("msgspec")
except ModuleNotFoundError as e:
    if e.name != "msgspec":
        raise
