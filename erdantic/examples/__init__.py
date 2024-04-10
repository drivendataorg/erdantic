"""Example data model classes."""

from erdantic.examples import dataclasses, pydantic, pydantic_v1

__all__ = [
    "dataclasses",
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
