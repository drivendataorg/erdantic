import sys
from typing import Type

if sys.version_info >= (3, 9):
    from functools import cache
else:
    from functools import lru_cache

    cache = lru_cache(maxsize=None)

from pydantic import BaseModel

# _PydanticBaseModelType = TypeVar("_PydanticBaseModelType", bound=)


def add_repr_pretty_to_pydantic(cls: Type[BaseModel]):
    """Decorator that adds a `_repr_pretty_` method to a Pydantic BaseModel subclass to enable
    pretty-printing in IPython.
    """

    def _repr_pretty_(self, p, cycle):
        """IPython special method to pretty-print an object."""
        try:
            # Rich supports Pydantic models, so use it if available
            import rich  # type: ignore [import-not-found]

            rich.print(self)
        except ModuleNotFoundError:
            if cycle:
                p.text(repr(self))
            else:
                # Pretty print using Pydantic special methods
                with p.group(2, f"{self.__repr_name__()}(", ")"):
                    for idx, (k, v) in enumerate(self.__repr_args__()):
                        if idx:
                            p.text(",")
                            p.breakable()
                        p.text(f"{k}=")
                        p.pretty(v)
                # p.breakable()
                # p.text(")")

    cls._repr_pretty_ = _repr_pretty_  # type: ignore [attr-defined]
    return cls


@cache
def ellipsis_arg_repr_factory(cls: type):
    """Factory function that produces a dummy class whose repr method returns the class signature
    with an ellipsis as its only argument. This is used to abbreviate the representation of a
    class instance.
    """

    class ReprDummy:
        """Dummy class with pretty-print special methods for IPython and Rich that replace init
        arguments with an ellipsis.
        """

        def __repr__(self) -> str:
            return f"{cls.__name__}(...)"

    ReprDummy.__name__ = cls.__name__

    return ReprDummy()


def sorteddict_repr_pretty(self, p, cycle):
    """IPython special method for pretty-printing a SortedDict."""
    try:
        # We also patch a __rich_repr__ method, so use that if rich is available
        import rich  # type: ignore [import-not-found]

        rich.print(self)
    except ModuleNotFoundError:
        if cycle:
            p.text(repr(self))
        else:
            # Pretty print argument as a dict
            with p.group(2, f"{self.__class__.__name__}(", ")"):
                p.pretty(dict(self))


def sorteddict_rich_repr(self):
    """Rich special method for pretty-printing a SortedDict."""
    # Pretty print argument as a dict
    yield dict(self)
