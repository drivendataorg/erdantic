from enum import Enum
from typing import Any, List, Type, Union

try:
    from typing import _GenericAlias as GenericAlias  # type: ignore # Python 3.7+

    # Note Python 3.9's types.GenericAlias != typing._GenericAlias
    # We still want typing._GenericAlias for typing module's deprecated capital generic aliases
except ImportError:
    from typing import GenericMeta as GenericAlias  # type: ignore # Python 3.6

try:
    from typing import Final  # type: ignore # Python 3.8+
except ImportError:
    from typing_extensions import Final  # type: ignore # noqa: F401 # Python 3.6-3.7


def _get_args(tp):
    """Backport of typing.get_args for Python 3.6"""
    return getattr(tp, "__args__", ())


def _get_origin(tp):
    """Backport of typing.get_origin for Python 3.6"""
    return getattr(tp, "__origin__", None)


try:
    from typing import get_args, get_origin  # type: ignore # Python 3.8+
except ImportError:
    try:
        from typing_extensions import get_args, get_origin  # type: ignore # Python 3.7
    except ImportError:
        # Python 3.6
        get_args = _get_args
        get_origin = _get_origin


def get_depth1_bases(tp: type) -> List[type]:
    """Returns depth-1 base classes of a type."""
    bases_of_bases = {bb for b in tp.__mro__[1:] for bb in b.__mro__[1:]}
    return [b for b in tp.__mro__[1:] if b not in bases_of_bases]


def get_recursive_args(tp: Union[type, GenericAlias]) -> List[type]:
    """Recursively finds leaf-node types of possibly-nested generic type."""

    def recurse(t):
        args = get_args(t)
        if args:
            for arg in args:
                yield from recurse(arg)
        else:
            yield t

    return list(recurse(tp))


def repr_type(tp: Union[type, GenericAlias]) -> str:
    """Return pretty, compact string representation of a type. Principles of behavior:

    - Names without module path
    - Generic capitalization matches which was used (`typing` module's aliases vs. builtin types)
    - Union[..., None] -> Optional[...]
    - Enums show base classes, e.g., `MyEnum(str, Enum)`
    """
    origin = get_origin(tp)
    if origin:
        origin_name = getattr(origin, "__name__", str(origin))
        args = get_args(tp)
        # Union[..., None] -> Optional[...]
        if origin is Union and args[-1] is type(None):  # noqa: E721
            origin_name = "Optional"
            args = args[:-1]
        # If generic alias from typing module, back out its name
        elif isinstance(tp, GenericAlias) and tp.__module__ == "typing":
            origin_name = str(tp).split("[")[0].replace("typing.", "")
        # Case for Python 3.6's wacky Union
        elif origin is Union:
            origin_name = "Union"
        return f"{origin_name}[{', '.join(repr_type(a) for a in args)}]"
    if tp is Ellipsis:
        return "..."
    if issubclass(tp, Enum):
        return repr_enum(tp)
    return tp.__name__


def repr_enum(tp: Type[Enum]) -> str:
    """Return pretty, compact string representation of an Enum type with its depth-1 base
    classes, e.g., `MyEnum(str, Enum)`."""
    depth1_bases = get_depth1_bases(tp)
    return f"{tp.__name__}({', '.join(b.__name__ for b in depth1_bases)})"


def repr_type_with_mro(obj: Any) -> str:
    """Return MRO of object if it has one. Otherwise return its repr."""

    def _full_name(tp: type) -> str:
        module = tp.__module__
        return f"{module}.{tp.__qualname__}".replace("builtins.", "")

    if hasattr(obj, "__mro__"):
        mro = ", ".join(_full_name(m) for m in obj.__mro__)
        return f"<mro ({mro})>"
    return repr(obj)
